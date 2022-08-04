import tkinter as tk
from tkinter import *
from tkinter import messagebox,filedialog
import tkinter.ttk
import pandas as pd
import openpyxl
import time
import shopping

root = tk.Tk()
root.title('판매자 정보 크롤링 서비스')
root.minsize(800, 300)  # 최소 사이즈
global sellerInfo, statusCode



# 기능1 : 조회하기
def get_data():
    listbox.delete(0, "end")
    global sellerInfo, statusCode
    sellerInfo = []
    start = time.time()
    sellerInfo, statusCode = shopping.getMalls(keyword.get(), startIndex.get(), endIndex.get())

    ''' 모든 수집이 완료되었을 때, 100%로 올림 '''
    shopping._CurrentProgress.set( 100 )
    shopping._ProgressBar.update()
    read_data(time.time()-start)


# 기능2 : 데이터 가져오기
def read_data(time):
    global sellerInfo,statusCode
    try:
        for data in sellerInfo:
            listbox.insert(END, list(data.values()))
        txtTotal.config(text="총 : " + str(len(sellerInfo)) + "개,  응답코드 : ["+str(statusCode)+"] , 소요시간 : "+str(time)[0:4]+"초")
    except:
        listbox.delete(0, "end")
        messagebox.showerror("Error", "오류가 발생했습니다.")


# 기능3: 엑셀로 다운로드
def download():
    try:
        reply = messagebox.askyesno("엑셀", "엑셀파일로 다운로드 하시겠습니까?")
        if reply:
            fileLocation = fileRoot.get()
            name = fileName.get()
            df = pd.DataFrame.from_records(sellerInfo)
            df.to_excel(excel_writer=str(fileLocation)+'/'+str(name)+'.xlsx')
            messagebox.showinfo("Success", "다운로드 되었습니다.")
    except Exception as e:
        messagebox.showerror("Error", "오류가 발생했습니다." + str(e))


# 기능4 : 저장할 위치 지정
def location():
    fileRoot.delete(0,'end')
    root.dirName = filedialog.askdirectory()
    fileRoot.insert(0,root.dirName)


'''1. 프레임 생성'''
# 상단 프레임 (LabelFrame)
frm1 = tk.LabelFrame(root, pady=15, padx=15)  # pad 내부
frm1.grid(row=0, column=0, pady=10, padx=10, sticky="nswe")  # pad 내부
root.columnconfigure(0, weight=1)  # 프레임 (0,0)은 크기에 맞춰 늘어나도록
root.rowconfigure(0, weight=1)
# 하단 프레임 (Frame)
frm2 = tk.Frame(root, pady=10)
frm2.grid(row=1, column=0, pady=10)

'''2. 요소 생성'''
# 레이블
lbl1 = tk.Label(frm1, text='검색어   ', pady= 10)
lblstart = tk.Label(frm1, text='시작 페이지   ')
lblend = tk.Label(frm1,text='종료 페이지  ')
lbl2 = tk.Label(frm1, text='결과   ')
lbl3 = tk.Label(frm1, text='저장 경로 선택   ')
txtTotal = tk.Label(frm1, text="총 0개")
lbl4 = tk.Label(frm1, text='파일 이름 입력   ', pady= 10)
script = tk.Label(frm1, text='입력하지 않을 경우, 시작 페이지 값 :1 , 종료 페이지 값 : 마지막', fg ='#E19C9C')
script2 = tk.Label(frm1, text='파일 경로와 파일 이름을 꼭 입력하세요.', fg ='#E19C9C')

# 엔트리
keyword = tk.Entry(frm1, width=40)
fileRoot = tk.Entry(frm1, width=40)
fileName = tk.Entry(frm1, width=40)
startIndex = tk.Entry(frm1,width=20)
endIndex = tk.Entry(frm1, width=20)

# 리스트박스
listbox = tk.Listbox(frm1, width=40, selectmode='extended')

# 버튼
btnInput = tk.Button(frm1, text="입력", width=8, command=get_data)
btnDownLoad = tk.Button(frm2, text="다운로드", width=8, command=download)
btnRoot = tk.Button(frm1, text="찾아보기", width=8, command=location)

'''3. 요소 배치'''
# 상단 프레임
lbl1.grid(row=0, column=0, sticky="e")
keyword.grid(row=0, column=1, columnspan=2, sticky="we")
btnInput.grid(row=0, column=3)

lblstart.grid(row=1, column=0, sticky='e')
startIndex.grid(row=1, column=1,  sticky='w')
lblend.grid(row=1, column=1 )
endIndex.grid(row=1, column=1 ,sticky='e')

script.grid(row=2, column=1, pady=(0,15), sticky='w')

lbl2.grid(row=3, column=0, sticky="en")
listbox.grid(row=3, column=1, rowspan=3, sticky="we")
txtTotal.grid(row=6, column=1, sticky="w",pady=(0,50))

lbl3.grid(row=7, column=0, sticky='n')
fileRoot.grid(row=7, column=1, columnspan=2, sticky="we")
btnRoot.grid(row=7, column=3)

lbl4.grid(row=8, column=0, sticky='n')
fileName.grid(row=8, column=1, columnspan=2, sticky='we')
script2.grid(row=9,column=1,sticky='w')

# 상단프레임 grid (2,1)은 창 크기에 맞춰 늘어나도록
frm1.rowconfigure(2, weight=1)
frm1.columnconfigure(1, weight=1)
btnDownLoad.pack()

'''4. progress bar 생성'''
frm_progress = tk.Frame(root,  pady=10 )
frm_progress.grid(row=2, column=0, pady=5)

CurrentProgress = tk.DoubleVar()
ProgressBar     = tkinter.ttk.Progressbar(frm_progress, maximum=100, variable=CurrentProgress);
ProgressBar.pack();


shopping._CurrentProgress = CurrentProgress
shopping._ProgressBar = ProgressBar

if __name__ == "__main__":
    root.mainloop()
