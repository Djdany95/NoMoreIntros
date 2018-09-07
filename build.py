import os

os.system('pyinstaller nomoreintros.spec --distpath ./NoMoreIntros')
os.system('C:/"Program Files"/7-Zip/7z.exe -mx=9 a "./NomoreIntrosPortable.zip" "./NoMoreIntros"')