import requests
from bs4 import BeautifulSoup as BS
import threading
import csv


class DetectThread(threading.Thread):

	def __init__(self, num, pool_divided, pool, func):
		threading.Thread.__init__(self)
		self.pool_divided = pool_divided[num]
		self.func = func
		self.pool = pool

	def run(self):
		for thing in self.pool_divided:
			res = self.func(thing)
			if res:
				self.pool.append(thing)
		global THREAD_IS_DONE
		THREAD_IS_DONE += 1
		return None


class ProxyIPs:

	def __init__(self, ip_population=30):
		self.small_ip_pool = []
		self.ip_pool = []
		self.ip_pop = ip_population
		self.total_good_ips = 0  # wait to be adjusted
		self.ip_pool_divided = []
		self.threads = []

	def get_ips(self, page_num=1):
		if page_num == 1:
			url = "http://www.xicidaili.com/nn/"
		else:
			url = "http://www.xicidaili.com/nn/" + str(page_num)
		headers = {
			"Host": "www.xicidaili.com",
			"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:46.0) Gecko/20100101 Firefox/46.0",
			"Connection": "keep-alive",
			"Referer": "http://www.xicidaili.com/nn/"
		}
		print("Getting ips of page %s" % str(page_num))
		response = requests.get(url, headers=headers)
		soup = BS(response.text, "html.parser")
		rawdata = soup.find_all("tr")
		for data in rawdata:
			sou = BS(str(data), "html.parser")
			_ip = sou.find_all("td")
			if _ip:
				ip = _ip[1].text
				port = _ip[2].text
				print("=="*30)
				print("IP:  %s" % ip + "    port: %s" % str(port))
				self.small_ip_pool.append({"ip": ip, "port": port})
		return None

	def detect_ip(self, thing):
		detect_url = "http://www.baidu.com"
		ip = thing["ip"]
		port = thing["port"]
		proxy_host = "http://" + ip + ":" + port
		try:
			res = requests.get(detect_url, proxies={"http": proxy_host}, timeout=3)
			if res.status_code == 200:
				print(ip + " is Good one.")
				self.total_good_ips += 1
				return True
			else:
				return False
		except:
			print(ip + " is Bad one.")
			return False

	def divide_pool(self, pool_name):
		thread_num = len(pool_name)//6
		for i in range(0, thread_num - 1):
			self.ip_pool_divided.append(pool_name[i*10:(i+1)*10])
		self.ip_pool_divided.append(pool_name[thread_num*10:])
		return None

	def detect_pool(self, pool_name):
		print("***"*20)
		print("Total good ips now %s" % str(self.total_good_ips))
		print("Detecting...")
		self.divide_pool(pool_name)
		global THREAD_IS_DONE
		THREAD_IS_DONE = 0
		for i in range(0, len(self.ip_pool_divided)):
			t = DetectThread(i, self.ip_pool_divided, self.ip_pool, self.detect_ip)
			self.threads.append(t)
		for t in self.threads:
			t.start()
		while True:
			if THREAD_IS_DONE == len(self.ip_pool_divided):
				THREAD_IS_DONE = 0
				self.threads = []
				self.ip_pool_divided = []
				break
			else:
				pass
		return None

	def initialize_ip_pool(self, save_ip=True):
		page_num = 1
		global THREAD_IS_DONE
		while self.total_good_ips <= self.ip_pop:
			self.get_ips(page_num=page_num)
			self.detect_pool(self.small_ip_pool)
			self.small_ip_pool = []
			page_num += 1
		print("======" + "  Finished with %s good ips.  " % str(self.total_good_ips) + "======")
		if save_ip:
			f = open("ip_pool.csv", "w", newline="")
			w = csv.writer(f)
			for thing in self.ip_pool:
				w.writerow([thing])
			f.close()
		return None

	def detect_saved_ips(self):
		f = open("ip_pool.csv", "r")
		r = csv.reader(f)
		for thing in r:
			self.small_ip_pool.append(eval(thing[0]))
		f.close()
		self.detect_pool(self.small_ip_pool)
		self.small_ip_pool = []
		return None


if __name__ == '__main__':
	p = ProxyIPs()
	p.detect_saved_ips()