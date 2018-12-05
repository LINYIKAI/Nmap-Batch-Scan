import os;
import xlrd;
import subprocess;
import re;
import logging;

def write_log():
    logger=logging.getLogger('log');#create logger object
    logger.setLevel(logging.DEBUG); #set logger level
    fh=logging.FileHandler('log.txt');  #create a handler,write to log.txt
    fh.setLevel(logging.DEBUG);
    sh=logging.StreamHandler(); #create a handler,wite to terminal
    sh.setLevel(logging.DEBUG);
    formatter=logging.Formatter('Logger: '+'%(asctime)s - %(name)s - %(levelname)s - %(message)s');#format must be defined
    fh.setFormatter(formatter);
    sh.setFormatter(formatter);
    logger.addHandler(fh);
    logger.addHandler(sh);
    return logger;



def read_excel(file_name):
    workbook=xlrd.open_workbook(file_name);
    table=workbook.sheet_by_index(0);
    column3=table.col_values(0);
    print(type(column3));
    return column3;



def nslookup(url,logger):
    out=subprocess.Popen('nslookup '+url+' && echo ok || echo no',stdout=subprocess.PIPE,shell=True);
    read_out=out.stdout.read().decode('utf-8');
    if 'ok' in read_out:
        ip_list=re.findall(r'\d+.\d+.\d+.\d+',read_out);
        logger.info(url+" nslookup sussess!\n");
        return ip_list[len(ip_list)-1];
    else:
        logger.warning(url+' nslookup error,find no ip address\n')
        return 0;


def nmap(url,ip,logger):
    if os.path.exists('nmap')==False:
        os.system('mkdir nmap');
    else:
        pass;
    try:
        out = subprocess.Popen('cd nmap && nmap -A  -Pn -sV -oN ' + url + '.xml ' + ip + ' && echo ok || echo no',stdout=subprocess.PIPE, shell=True);
        read_out = out.stdout.read().decode('utf-8');
        if 'ok' in read_out:
            logger.info(url+' nmap scan success!\n');
            print(read_out);
    except:
        logger.warning(url+' nmap scan error\n')


if __name__=='__main__':
    logger = write_log();
    url_list=read_excel('test.xlsx');
    for url in url_list:
        if url != '':#no blank
            url = url.replace(' ','');
            url=url.rstrip('/');
            if 'http://' in url or 'https://' in url:
                http_s = re.findall(r'.*//',url);
                url = url.replace(http_s[0], '');
            regex_ip=re.findall(r'\d+.\d+.\d+.\d{1,3}',url);
            if regex_ip==[]:#not ip
                regex_port=re.findall(r':\d{1,5}',url);
                if regex_port==[]:#no port
                    if url.count('/')>=1:
                        url=url.split('/')[0];
                        url_response = nslookup(url, logger);
                        if type(url_response) == str:
                            nmap(url, url_response, logger);
                    else:
                        url_response = nslookup(url, logger);
                        if type(url_response) == str:
                            nmap(url, url_response, logger);
                else:#url with port number
                    url=url.split(regex_port[0])[0];
                    url_response=nslookup(url, logger);
                    if type(url_response)==str:
                        nmap(url, url_response, logger);
            else:#url contain ip address
                url=url.replace('/','');
                nmap(url,regex_ip[0],logger);
        else:
            pass;
