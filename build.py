import os

os.system('pyinstaller nomoreintroslight.spec')
os.system('C:/"Program Files"/7-Zip/7z.exe -mx=9 a "./NomoreIntrosLight.zip" "./dist/NoMoreIntrosLight"')

os.system('pyinstaller nomoreintrosdark.spec')
os.system('C:/"Program Files"/7-Zip/7z.exe -mx=9 a "./NomoreIntrosDark.zip" "./dist/NoMoreIntrosDark"')
