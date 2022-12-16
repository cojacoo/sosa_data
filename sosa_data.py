import streamlit as st
import ftplib
import numpy as np
import pandas as pd

# Fill Required Information
HOSTNAME = "ftp.drivehq.com"
USERNAME = "cojacoo"

def load_data(pwd, nrows=-25):
    # Connect FTP Server
    ftp_server = ftplib.FTP("ftp.drivehq.com", "cojacoo", pwd)
 
    # force UTF-8 encoding
    ftp_server.encoding = "utf-8"

    files = ftp_server.nlst()
    fis = pd.Series(files).loc[pd.Series(files).str.contains('Sosa')]
    dummy = pd.DataFrame(np.stack(fis.str.split('_').values))
    fis.index = pd.to_datetime(dummy[4]+dummy[5].str.slice(0,6),format='%y%m%d%H%M%S')
    fis = fis.sort_index().iloc[nrows:]

    firstitem = True

    for t in fis.index:
        gFile = open("dummy.csv", "wb")
        ftp_server.retrbinary('RETR '+fis.loc[t], gFile.write)
        gFile.close()
    
        dummy = pd.read_csv('dummy.csv', sep=';', decimal=',',skiprows=2)
    
        if firstitem:
            data = dummy
            firstitem = False
        else:
            data = pd.concat([data, dummy], axis=0)
        
        data.index = pd.to_datetime(data.DATE+' '+data.TIME)
    
    return data

st.title('Sosa Weather')
pwd = st.sidebar.text_input("Enter password 👇")

st.sidebar.write('Select last records')
nrows = st.sidebar.slider('last #', -30, -2, -15)

if pwd:
    data = load_data(pwd, nrows)

colx = st.radio("Select variable", ('RH', 'Temp', 'Rain'))

if colx=='Temp':
    st.line_chart(data.Temp)
elif colx=='RH':
    st.line_chart(data.RH)
else:
    st.line_chart(data.Rainmm)