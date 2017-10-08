DEFAULT_KEY = '123nwh2oos-93kkowed8!@$&(w8357'

def EnCrypt_Str( arg_s, arg_key ):
    i = 1
    s = ''
    if arg_key == '':
        arg_key = DEFAULT_KEY
    for c in arg_s:
        c = ( ( ord( c ) + ord( arg_key[i] ) % 255 ) )
        i=i+1
        if i > len(arg_key) - 1:
            i = 1
        c = chr(c)
        s = s + c

    return s.encode('utf-8')

def DeCrypt_Str( arg_s, arg_key ):
    arg_s = arg_s.decode('utf-8')
    i = 1
    s = ''
    if arg_key == '':
        arg_key = DEFAULT_KEY
    for c in arg_s:
        c = ( ( ord( c ) - ord( arg_key[i] ) % 255 ) )
        i=i+1
        if i > len(arg_key) - 1:
            i = 1
        c = chr(c)
        s = s + c

    return s