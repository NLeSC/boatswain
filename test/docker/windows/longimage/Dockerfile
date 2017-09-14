FROM microsoft/nanoserver

ENV IMAGE=longimage

# Create a Temp folder
RUN New-Item `-Path "C:\Temp" ` -Type directory ;

# Download Python 3.5.2 Windows x64 to C:\Temp
RUN Invoke-WebRequest ` -Uri "https://www.python.org/ftp/python/3.5.2/python-3.5.2-embed-amd64.zip" ` -OutFile "C:\Temp\python-3.5.2-embed-amd64.zip" ;

CMD ["Get-Childitem -Path Env:* | Sort-Object Name"]