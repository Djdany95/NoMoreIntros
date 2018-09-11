# -*- mode: python -*-

block_cipher = None


a = Analysis(['NoMoreIntros.py'],
             pathex=['./'],
             binaries=[],
             datas=[( './bin', './bin' ), ( './lang', './lang' ), ( 'NoMoreIntros.ico', '.' )],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='NoMoreIntros',
          debug=False,
          strip=False,
          upx=True,
          console=False, icon='NoMoreIntros.ico' )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='NoMoreIntros')
