from urllib.request import Request, urlopen
from bs4 import BeautifulSoup

def get_jpy_exchange_rate():
    # 臺灣銀行牌告匯率網頁
    url = 'https://rate.bot.com.tw/xrt?Lang=zh-TW'
    request = Request(url, headers={'User-Agent': 'Mozilla/5.0'})

    try:
        with urlopen(request, timeout=10) as response:
            # 條件式 if：檢查 HTTP 狀態碼是否成功
            if response.status != 200:
                print(f'無法取得網頁資料 (HTTP 狀態碼: {response.status})')
                return None
            html = response.read()
    except Exception as error:
        print(f'連線發生錯誤: {error}')
        return None

    soup = BeautifulSoup(html, 'html.parser')
    
    # 直接抓取網頁中所有的表格橫列 tr
    rows = soup.find_all('tr')
    
    for row in rows:
        row_text = row.get_text()
        
        # 條件式 if：利用條件篩選出包含「日圓」或「JPY」的的那一行
        if '日圓' in row_text or 'JPY' in row_text:
            cols = row.find_all('td')
            # 確保欄位數量足夠（臺銀現金賣出通常在第 3 個欄位，index 為 2）
            if len(cols) >= 3:
                try:
                    cash_sell_rate = cols[2].get_text(strip=True)
                    return float(cash_sell_rate)
                except ValueError:
                    continue
                    
    print('找不到日圓匯率欄位資料')
    return None

def main():
    print('正在取得台銀最新日圓匯率...')
    rate = get_jpy_exchange_rate()
    
    # 條件式 if：檢查是否成功抓到匯率數值
    if rate is None:
        print('無法取得日圓匯率，程式終止。')
        return

    print(f'成功取得！目前台銀日圓現金賣出匯率為: {rate}')
    print('----------------------------------------')
    
    # 讓使用者選擇換算方向
    choice = input('請選擇換算方向 (輸入 1 代表「台幣換日圓」，輸入 2 代表「日圓換台幣」): ')
    
    # 條件式 if / elif / else：判斷使用者的輸入選項執行對應的換算邏輯
    if choice == '1':
        twd = float(input('請輸入你想使用的台幣金額 (TWD): '))
        jpy = twd / rate
        print(f'使用 {twd} 元台幣，大約可以換到 {jpy:.2f} 日圓。')
        
    elif choice == '2':
        jpy = float(input('請輸入你想換回的日圓金額 (JPY): '))
        twd = jpy * rate
        print(f'使用 {jpy} 日圓，大約可以換回 {twd:.2f} 元台幣。')
        
    else:
        print('輸入錯誤！請重新執行程式並輸入正確的選項（1 或 2）。')

if __name__ == '__main__':
    main()