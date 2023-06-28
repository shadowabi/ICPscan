package cmd

import (
	"os"
	"github.com/spf13/cobra"
	"strings"
	"sync"
	exec "github.com/shadowabi/ICPscan/pkg"
)

var (
	file	  string
	url		  string
)


var RootCmd = &cobra.Command{
	Use:   	"ICPscan",
	Short: 	"",
	Long: 	"",
}

func init() {
	RootCmd.CompletionOptions.DisableDefaultCmd = true
	RootCmd.Flags().StringVarP(&file, "file", "f", "", "从文件中读取目标地址 (Input FILENAME)")
	RootCmd.Flags().StringVarP(&url, "url", "u", "", "输入目标地址 (Input IP/DOMAIN/URL)")
}

func Execute(){
	err := RootCmd.Execute()

	var wg sync.WaitGroup
    if url != "" {
    	wg.Add(1)
        go exec.Scan(strings.TrimSpace(url), &wg)
        wg.Wait()
    } else if file != "" {
        exec.ReadFile(file)
    } else {
    	RootCmd.Usage()
    }

    if len(exec.Rs) != 0 {
    	exec.OutPut()
    }

	if err != nil {
		os.Exit(1)
	}
}