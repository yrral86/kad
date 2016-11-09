def webcawler(keyword):
    print keyword
    import os
    from selenium import webdriver
    from selenium.webdriver.support.ui import WebDriverWait
    driver = webdriver.Firefox(executable_path = '/home/shifu/Downloads/geckodriver')
    driver.execute_script("Liunx.scrollTo(0, document.body.scrollHeight);")
    driver.get('http://scholar.google.com')
    inputElement = driver.find_element_by_name("q")
    inputElement.send_keys(keyword)
    inputElement.submit()
    currentURL=driver.current_url
    urlList=[]
    localDir = 'down_pdf\\'
    fileOut = localDir + searchWord + ".txt"
    import urllib, re,codecs,sys
    fileOp = codecs.open(fileOut, 'a', sys.getdefaultencoding())
    for i in range(0,10):
        pdf_url = driver.find_elements_by_css_selector("a")
        for k in pdf_url:
            try:
                z= k.get_attribute("href")
                if '.pdf' in z and z not in urlList:
                    urlList.append(z)
                    print z
            except:
                import time
                time.sleep(1)
                continue
        contents=driver.find_elements_by_css_selector('h3')
        for ct in contents:
            print ct.text
            
        driver.get(currentURL+"&start="+str(i*10)+"&as_sdt=0,5&as_ylo=2008")
        import time
        time.sleep(3)
    print len(urlList)

    for everyURL in urlList:                                 
            wordItems = everyURL.split('/')                   
            for item in wordItems:                            
                    if re.match('.*\.pdf$', item):            
                            PDFName = item                  
            localPDF = localDir +searchWord+"_"+ PDFName                   
            try:
                    urllib.urlretrieve(everyURL, localPDF)   
            except Exception,e:
                    continue
    
