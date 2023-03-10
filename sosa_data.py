import streamlit as st
import ftplib
import numpy as np
import pandas as pd
import plotly.express as px

# Fill Required Information
HOSTNAME = "ftp.drivehq.com"
USERNAME = "cojacoo"

@st.cache
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

colx = st.sidebar.radio("Select variable", ('RH', 'Temp', 'Rain'))

if st.button('Plot data'):
    if pwd:
        data = load_data(pwd, nrows)
    if colx=='Temp':
        fig = px.line(data.Temp, template='none')
    elif colx=='RH':
        fig = px.line(data.RH, template='none')
    else:
        fig = px.line(data.Rainmm, template='none')
    st.plotly_chart(fig, theme=None, use_container_width=True)
else:
    st.write('👈 Make selections')

