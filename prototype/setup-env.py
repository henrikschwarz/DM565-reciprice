MONGO_URI = 'mongodb://%s:%s@pratgen.dk:27017/innovation?authSource=innovation'

print('Please enter your mongodb credentials.')
print('Username:')
username = input()
print('\nPassword')
password = input()

f = open('.env','w')
f.write('MONGO_URI=' + (MONGO_URI % (username, password)))
f.close()

print('\n.env file updated! Press enter to continue...')
input()