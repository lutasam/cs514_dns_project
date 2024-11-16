//package main
//
//import (
//	"fmt"
//	"log"
//	"sync"
//	"time"
//
//	"github.com/miekg/dns"
//	"github.com/patrickmn/go-cache"
//)
//
//var (
//	dnsCache    *cache.Cache
//	cacheMutex  sync.RWMutex
//	cacheTTL    = 10 * time.Minute
//	cachePurge  = 15 * time.Minute
//	upstreamDNS = "8.8.8.8:53"
//)
//
//
//func init() {
//	dnsCache = cache.New(cacheTTL, cachePurge)
//}
//
//
//func queryDNS(question dns.Question) *dns.Msg {
//	cacheKey := fmt.Sprintf("%s-%d", question.Name, question.Qtype)
//
//	
//	cacheMutex.RLock()
//	if cached, found := dnsCache.Get(cacheKey); found {
//		cacheMutex.RUnlock()
//		return cached.(*dns.Msg)
//	}
//	cacheMutex.RUnlock()
//
//
//	client := new(dns.Client)
//	msg := new(dns.Msg)
//	msg.SetQuestion(question.Name, question.Qtype)
//
//	response, _, err := client.Exchange(msg, upstreamDNS)
//	if err != nil {
//		log.Printf("Failed to query upstream DNS: %s", err)
//		return nil
//	}
//
//
//	cacheMutex.Lock()
//	dnsCache.Set(cacheKey, response, cache.DefaultExpiration)
//	cacheMutex.Unlock()
//
//	return response
//}
//
//
//func handleDNSQuery(w dns.ResponseWriter, r *dns.Msg) {
//	msg := new(dns.Msg)
//	msg.SetReply(r)
//	msg.Compress = true
//
//	for _, question := range r.Question {
//		switch question.Qtype {
//		case dns.TypeA, dns.TypeAAAA, dns.TypeCNAME:
//
//			response := queryDNS(question)
//			if response != nil {
//				msg.Answer = append(msg.Answer, response.Answer...)
//			}
//		default:
//
//			msg.SetRcode(r, dns.RcodeNotImplemented)
//		}
//	}
//
//
//	if err := w.WriteMsg(msg); err != nil {
//		log.Printf("Failed to write response: %s", err)
//	}
//}
//
//func main() {
//
//	dns.HandleFunc(".", handleDNSQuery)
//
//	udpServer := &dns.Server{Addr: ":8053", Net: "udp"}
//	go func() {
//		log.Println("Starting UDP DNS server on :8053")
//		if err := udpServer.ListenAndServe(); err != nil {
//			log.Fatalf("Failed to start UDP server: %s", err)
//		}
//	}()
//
//	tcpServer := &dns.Server{Addr: ":8053", Net: "tcp"}
//	go func() {
//		log.Println("Starting TCP DNS server on :8053")
//		if err := tcpServer.ListenAndServe(); err != nil {
//			log.Fatalf("Failed to start TCP server: %s", err)
//		}
//	}()
//
//	select {}
//}

package main

import (
	"crypto/tls"
	"fmt"
	"io"
	"log"
	"net/http"
	"sync"
	"time"

	"github.com/miekg/dns"
	"github.com/patrickmn/go-cache"
)


var (
	dnsCache    *cache.Cache
	cacheMutex  sync.RWMutex
	cacheTTL    = 10 * time.Minute
	cachePurge  = 15 * time.Minute
	upstreamDNS = "8.8.8.8:53"
)

func init() {
	dnsCache = cache.New(cacheTTL, cachePurge)
}

func queryDNS(question dns.Question, dnssec bool) *dns.Msg {
	cacheKey := fmt.Sprintf("%s-%d", question.Name, question.Qtype)

	cacheMutex.RLock()
	if cached, found := dnsCache.Get(cacheKey); found {
		cacheMutex.RUnlock()
		return cached.(*dns.Msg)
	}
	cacheMutex.RUnlock()

	client := new(dns.Client)
	client.UDPSize = 4096
	msg := new(dns.Msg)
	msg.SetQuestion(question.Name, question.Qtype)
	if dnssec {
		msg.SetEdns0(4096, true)
	}

	response, _, err := client.Exchange(msg, upstreamDNS)
	if err != nil {
		log.Printf("Failed to query upstream DNS: %s", err)
		return nil
	}

	cacheMutex.Lock()
	dnsCache.Set(cacheKey, response, cache.DefaultExpiration)
	cacheMutex.Unlock()

	return response
}

func handleDNSQuery(w dns.ResponseWriter, r *dns.Msg) {
	msg := new(dns.Msg)
	msg.SetReply(r)
	msg.Compress = true

	for _, question := range r.Question {
		response := queryDNS(question, false)
		if response != nil {
			msg.Answer = append(msg.Answer, response.Answer...)
			msg.Extra = append(msg.Extra, response.Extra...)
		}
	}

	if err := w.WriteMsg(msg); err != nil {
		log.Printf("Failed to write response: %s", err)
	}
}

func dohHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	body, err := io.ReadAll(r.Body)
	if err != nil {
		http.Error(w, "Failed to read request body", http.StatusInternalServerError)
		return
	}

	msg := new(dns.Msg)
	if err := msg.Unpack(body); err != nil {
		http.Error(w, "Failed to parse DNS query", http.StatusBadRequest)
		return
	}

	response := new(dns.Msg)
	response.SetReply(msg)
	for _, question := range msg.Question {
		res := queryDNS(question, true)
		if res != nil {
			response.Answer = append(response.Answer, res.Answer...)
			response.Extra = append(response.Extra, res.Extra...)
		}
	}

	data, err := response.Pack()
	if err != nil {
		http.Error(w, "Failed to pack DNS response", http.StatusInternalServerError)
		return
	}
	w.Header().Set("Content-Type", "application/dns-message")
	w.WriteHeader(http.StatusOK)
	w.Write(data)
}

func main() {
	dns.HandleFunc(".", handleDNSQuery)
	udpServer := &dns.Server{Addr: ":8053", Net: "udp"}
	tcpServer := &dns.Server{Addr: ":8053", Net: "tcp"}

	go func() {
		log.Println("Starting UDP DNS server on :8053")
		if err := udpServer.ListenAndServe(); err != nil {
			log.Fatalf("Failed to start UDP server: %s", err)
		}
	}()

	go func() {
		log.Println("Starting TCP DNS server on :8053")
		if err := tcpServer.ListenAndServe(); err != nil {
			log.Fatalf("Failed to start TCP server: %s", err)
		}
	}()

	http.HandleFunc("/dns-query", dohHandler)
	server := &http.Server{
		Addr: ":4443",
		TLSConfig: &tls.Config{
			MinVersion: tls.VersionTLS12,
		},
	}
	go func() {
		log.Println("Starting DoH server on :4443")
		if err := server.ListenAndServeTLS("cert.pem", "key-decrypted.pem"); err != nil {
			log.Fatalf("Failed to start DoH server: %s", err)
		}
	}()

	select {}
}
