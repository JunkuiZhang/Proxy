import requests
from bs4 import BeautifulSoup as BS


class ProxyIPs:

	def __init__(self):
		self.ip_pool = []

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
		response = requests.get(url, headers=headers)
		soup = BS(response.text, "html.parser")
		rawdata = soup.find_all("tr")
		for data in rawdata:
			sou = BS(str(data), "html.parser")
			_ip = sou.find_all("td")
			if _ip:
				ip = _ip[1].text
				print("=="*30)
				print("IP:  %s" % ip)
				self.ip_pool.append(ip)
		return None


if __name__ == '__main__':
	p = ProxyIPs()
	print(p.get_ips())