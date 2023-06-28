package pkg

import (
"bufio"
"fmt"
"net/http"
"os"
"regexp"
"strings"
"sync"
"time"
"io/ioutil"
"crypto/tls"

"github.com/PuerkitoBio/goquery"
)


var (
	userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4621.0 Safari/537.36"
	icp = "https://icplishi.com/"
	flag = 0
	ICPnumber string
	Rs []string // 存放域名结果
	client = &http.Client{ //http.client
		Timeout: 5 * time.Second,
		Transport: &http.Transport{
			TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
		},
	}
	mu sync.Mutex
)

func OutPut() {
	if len(Rs) == 0 {
		return
	}
	file, err := os.OpenFile("./result.txt", os.O_WRONLY|os.O_CREATE|os.O_TRUNC, 0644)
    if err != nil {
        panic(err)
    }
    defer file.Close()

    writer := bufio.NewWriter(file)
    defer writer.Flush()

	fmt.Println("子域名：")
	for _, v := range Rs {
		fmt.Println("[+] " + v)
		fmt.Fprintln(writer, v)
	}
	fmt.Println("已保存到result.txt文件")
}

func ReadFile(filename string) {
    file, err := os.Open(filename)
    if err != nil {
        fmt.Println("无法打开此文件")
        os.Exit(1)
    }
    scan := bufio.NewScanner(file)
    var wg sync.WaitGroup
    for scan.Scan() {
        line := strings.TrimSpace(scan.Text())
        wg.Add(1)
        go Scan(line, &wg)
        wg.Wait()
    }
    wg.Wait()
    file.Close()
}

func Check(url string) string {
	if match, _ := regexp.MatchString(`(http|https)\:\/\/`, url); match { // 当输入 URL 时提取出域名
		url = regexp.MustCompile(`(http|https)\:\/\/`).ReplaceAllString(url, "")
		if match, _ := regexp.MatchString(`(\/|\\).*`, url); match {
			url = regexp.MustCompile(`(\/|\\).*`).ReplaceAllString(url, "")
		}
	}
	if match, _ := regexp.MatchString(`^([a-zA-Z0-9]([a-zA-Z0-9-_]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,11}$`, url); match { // 匹配域名
		flag = 1 // 域名
		return url
	}
	if match, _ := regexp.MatchString(`.ICP.\d{6,}.`, url); match {
		if match, _ := regexp.MatchString(`.ICP.\d{6,}.-\d{1,}`, url); match {
			url = regexp.MustCompile(`-\d{1,}`).ReplaceAllString(url, "") // 提取主备案号
		}
		ICPnumber = url
		flag = 2 // 备案号
		return url
	}
	return ""
}

func GetDomain(html string) {
	doc, err := goquery.NewDocumentFromReader(strings.NewReader(html))
	if err != nil {
		return
	}

	doc.Find("body > div > div.container > div > div.module.mod-panel > div > div:nth-child(2) > div.c-bd > div").Each(func(i int, s *goquery.Selection) {
		text := s.Text()
		text = strings.TrimSpace(text)
		matches := regexp.MustCompile(`.*\w+\.\w+`).FindAllString(text, -1)
		for _, match := range matches {
			if match != "" && !contains(Rs, match) {
				Rs = append(Rs, match)
			}
		}
	})
}

func GetICP(html string) {
	doc, err := goquery.NewDocumentFromReader(strings.NewReader(html))
	if err != nil {
		return
	}

	doc.Find("body > div > div.container > div > div.module.mod-panel > div.bd > div:nth-child(2) > div.c-bd").Each(func(i int, s *goquery.Selection) {
		text := s.Text()
		text = strings.TrimSpace(text)
		re := regexp.MustCompile(`.ICP.\d{6,}.`)
		match := re.FindString(text)
		if match != "" {
			ICPnumber = match
		}
	})
}

func Scan(url string, wg *sync.WaitGroup) {
	defer wg.Done()
	mu.Lock()
	defer mu.Unlock()

	url = Check(url)
	if url == "" {
		return
	}

	url = icp + url

	req, _ := http.NewRequest("GET", url, nil)
	req.Header.Set("User-Agent", userAgent)
	resp, err := client.Do(req)
	if err != nil {
		err.Error()
		return
	}
	defer resp.Body.Close()

	if flag == 1 {
		GetICP(GetResponseBody(resp)) //通过域名提取ICP号
	}
	url = icp + ICPnumber
	req, _ = http.NewRequest("GET", url, nil)
	req.Header.Set("User-Agent", userAgent)
	resp, err = client.Do(req)
	if err != nil {
		err.Error()
		return
	}
	defer resp.Body.Close()

	GetDomain(GetResponseBody(resp))
	flag = 0
}

func GetResponseBody(resp *http.Response) string{
	if resp.Body != nil {
		body, _ := ioutil.ReadAll(resp.Body)
		return string(body)
	}
	return ""
}

func contains(arr []string, str string) bool {
	for _, a := range arr {
		if a == str {
			return true
		}
	}
	return false
}