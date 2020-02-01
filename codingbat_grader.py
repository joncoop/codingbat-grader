"""
ZipGrade Reporter is a tool that can process the CSV Export data from ZipGrade
and use it to generate reports in a Microsoft Word format. Reports contain
detailed test statistics, score summaries by class, and individual score reports
for distribution to students.
"""

import os
import sys
import requests
import webbrowser

from bs4 import BeautifulSoup
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from tkinter import *
from tkinter.ttk import *

if getattr(sys, 'frozen', False):
    application_path = sys._MEIPASS + '/'
else:
    application_path = os.path.dirname(__file__) + '/'

software_version = 'v0.9-beta.1'
"""str: Version number of this release."""

version_url = 'https://raw.githubusercontent.com/joncoop/zipgrade-reporter/master/src/version.txt'
""" str: URL of version info, used to check if software is up-to-date."""

help_url = "https://joncoop.github.io/codingbat-grader/"
"""str: Support website."""


# Account info
LOGIN_URL = "https://codingbat.com/login"
REPORT_URL = "https://codingbat.com/report?java=on&python=on&stock=on&sortname=on"
SSL_VERIFY = False

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class App:
    """
    GUI component of CodingBat Grader.

    Attributes:
        import_path (str): Path to CSV file.
        export_path (str): Path to save final report.
    """

    def __init__(self, master):
        """Constructor for an App
        """
        
        self.data_table = None
        self.headers = []
        self.problem_sets = []
        self.students = []
        self.logged_in = False
        
        self.master = master
        self.gui_init()

    def gui_init(self):
        """
        Defines App layout
        """
        #self.master.iconbitmap(application_path + 'images/icon.ico')
        self.master.title("CodingBat Grader")
        self.master.resizable(True, True)

        Label(self.master, text='User ID').grid(row=0, column=0)
        un = StringVar()
        self.uname_entry = Entry(self.master, textvariable=un, width=30)
        self.uname_entry.grid(row=0, column=1)
        
        Label(self.master, text='Password').grid(row=0, column=2)
        pw = StringVar()
        self.pw_entry = Entry(self.master, show="\u2022" ,textvariable=pw) 
        self.pw_entry.grid(row=0, column=3) 

        login_button = Button(self.master, text="Log in", command=self.login)
        login_button.bind('<Return>', lambda e: self.login())
        login_button.grid(row=0, column=4, padx=5, pady=5, sticky=(E))

        sep = Separator(self.master, orient=HORIZONTAL).grid(row=1, columnspan=5, sticky='EW')

        problems_lbl = Label(self.master, text="Problem Sets")
        problems_lbl.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky=(W))

        Label(self.master, text='Memo Filter').grid(row=2, column=2)
        filter_str = StringVar()
        filter_str.set("")
        filter_str.trace("w", filter_str.get())
        
        sv = StringVar()
        sv.trace("w", lambda name, index, mode, sv=sv: self.show_students())
        self.filter_entry = Entry(self.master, textvariable=sv)
        self.filter_entry.grid(row=2, column=3, padx=5, pady=5) 
        
        self.problem_set_menu = Listbox(self.master, height=36, exportselection=False)
        self.problem_set_menu.bind('<<ListboxSelect>>', lambda e: self.show_students())
        self.problem_set_menu.grid(row=3, column=0, padx=5, pady=5, sticky=(N))

        cols = ('Username', 'Memo', 'Score')
        self.student_list = Treeview(self.master, columns=cols, height=32, show='headings')

        for col in cols:
            self.student_list.heading(col, text=col)  
        self.student_list.grid(row=3, column=1, columnspan=4, padx=5, pady=5)

        
        links = Frame(self.master)
        
        help_link = Label(links, text="Help", foreground="blue", cursor="hand2")
        help_link.pack( side = LEFT )
        help_link.bind("<Button-1>", lambda e: webbrowser.open_new(help_url))

        '''
        if not self.is_up_to_date():
            slash = Label(links, text=" | ", foreground="gray", cursor="hand2")
            slash.pack( side = LEFT )
                    
            update_link = Label(links, text="Update CodingBat Grader", foreground="blue", cursor="hand2")
            update_link.pack( side = LEFT )
            update_link.bind("<Button-1>", lambda e: webbrowser.open_new(help_url))
        '''
        
        links.grid(row=4, column=0, columnspan=3, padx=5, pady=5, sticky=(W))

        version = Label(self.master, text=software_version, foreground="gray")
        version.grid(row=4, column=4, columnspan=1, padx=5, pady=5, sticky=(E))
        

    def is_up_to_date(self):
        """
        Checks the CodingBat Grader website to see if application is latest version.

        Returns:
            True if up-to-date, False otherwise
        """

        try:
            fp = urllib.request.urlopen(version_url)
            mybytes = fp.read()
            version_txt = mybytes.decode('utf8')
            fp.close()

            start_del = "StringStruct(u'FileVersion', u'"
            end_del = "'),"

            start_loc = version_txt.find(start_del) + len(start_del)
            end_loc = version_txt.find(end_del, start_loc)

            version = 'v' + version_txt[start_loc: end_loc]

            if version == software_version:
                return True
        except:
            pass
        
        return False
    
    def login(self):
        """
        Does something.
        """

        with requests.Session() as s:
            page = s.get(REPORT_URL, verify=SSL_VERIFY)
            
            payload = {"uname": self.uname_entry.get(),
                       "pw": self.pw_entry.get()}
            
            response = s.post(LOGIN_URL, verify=SSL_VERIFY, data=payload)
            html = s.get(REPORT_URL).content

        self.logged_in = '[<a href=/logout>log out</a>]' in str(html)

        if self.logged_in:
            soup = BeautifulSoup(html, "html.parser")
            self.data_table = soup.findAll('table')[2] # the third table is the student scores

            rows = self.data_table.findAll('tr')
            header_row = rows[0]
            th_elements = header_row.findAll('th')

            self.headers = []
            for th in th_elements:
                self.headers.append(th.get_text().strip())

            self.problem_sets = self.headers[2:]
            self.show_problem_sets()
            
            self.students = []

            for row in rows[2:]:
                td_elements = row.findAll('td')

                student = []
                for i, td in enumerate(td_elements):
                    student.append(td.get_text())
                self.students.append(student)

            self.show_students()
        else:
            print("login failed")
    
    def show_problem_sets(self):
        """
        Does something.
        """
        for i, ps in enumerate(self.problem_sets):
            self.problem_set_menu.insert(i, ps) 
        
    def show_students(self):
        """
        Does something.
        """

        if self.logged_in:
            self.student_list.delete(*self.student_list.get_children())
            selected_problem_sets = self.problem_set_menu.curselection()

            if not selected_problem_sets is ():
                index = selected_problem_sets[0]
            else:
                index = None
                
            memo_filter = self.filter_entry.get()
            memo_filter.lower()

            i = 0
            for stu in self.students:
                user = stu[0]
                memo = stu[1]

                if index is not None:
                    score = stu[index + 2]
                else:
                    score = ''

                if memo_filter in memo.lower():
                    #self.student_list.insert(END, f'{memo:30s} {score}\n')
                    
                    self.student_list.insert("", "end", values=(user, memo, score))

        
# Let's do this!
if __name__ == "__main__":
    root = Tk()
    my_gui = App(root)
    root.mainloop()
