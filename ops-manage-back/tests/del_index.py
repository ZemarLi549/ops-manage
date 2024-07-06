verify_str = '-u aops:1qaZwsx3edcrfv'
host = '10.110.1.11:9113'
awk_str = ''
del_str = 'aops-tengine-tengine'
cmd = shell_str = " curl " + verify_str + " -X GET -s 'http://" + host + "/_cat/indices?v&s=store.size:desc'" + awk_str + "|grep -E '" + del_str + "'"
print(cmd)


