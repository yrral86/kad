def webcawler2(keyword,pagenum,year):
    print "llalalala "
    import os
    from selenium import webdriver
    from selenium.webdriver.support.ui import WebDriverWait
    driver = webdriver.Firefox(executable_path = '/home/shifu/Downloads/geckodriver')
    driver.get('http://jurn.org/')
    inputElement = driver.find_element_by_name("search")
    inputElement.send_keys(keyword+" pdf")
    inputElement.submit()
    currentURL=driver.current_url
    urlList=[]
    localDir = '/home/shifu/Downloads/kad-larry/pdf/'
    fileOut = localDir + keyword + ".txt"
    import urllib, re,codecs,sys
    fileOp = codecs.open(fileOut, 'a', sys.getdefaultencoding())
    driver.get(currentURL+"?search="+keyword+"+pdf"+"#gsc.tab=0&gsc.q="+keyword+"+pdf&gsc.sort=&gsc.page=1")
    import time
    time.sleep(5)
    for i in range(0,int(pagenum)):
        pdf_url = driver.find_elements_by_css_selector("a")
	print len(pdf_url)
        for k in pdf_url:
            try:
		print k
                z= k.get_attribute("href")
		import time
                time.sleep(1)
		print z
                if '.pdf' in z and z not in urlList:
                    urlList.append(z)
                    print z
            except:
                import time
                time.sleep(1)
                continue
       # contents=driver.find_elements_by_class_name('gs-title gsc-table-cell-thumbnail gsc-thumbnail-left')
       # for ct in contents:
       #     print ct.text
  
       # driver.get(currentURL+"#gsc.tab=0&gsc.q="+keyword+"+pdf"+"&gsc.sort=&gsc.page="+str(i+1))
        import time
        time.sleep(3)
    print len(urlList)

    for everyURL in urlList:                                 
            wordItems = everyURL.split('/')                   
            for item in wordItems:                            
                    if re.match('.*\.pdf$', item):            
                            PDFName = item                  
            localPDF = localDir +keyword+"_"+ PDFName                   
            try:
                    urllib.urlretrieve(everyURL, localPDF)   
            except Exception,e:
                    continue
    
