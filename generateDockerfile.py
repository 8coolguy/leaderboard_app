f = open('keys.env', 'r')
vs = f.readlines()

dockerFile = open('api/Dockerfile','w')
cmds = [
 	"FROM python:3.10-slim-buster\n",
  	"COPY requirements.txt requirements.txt\n",
  	"RUN pip install --upgrade pip\n"
]+["ENV" + v[6:] for v in vs]+[
	"WORKDIR /app\n",
 	 "COPY . /app\n",
  	"RUN pip --no-cache-dir install -r requirements.txt\n",
  	'''CMD ["flask", "run","--host","0.0.0.0"]\n''',
	"EXPOSE 5000\n"
]

dockerFile.writelines(cmds)
dockerFile.close()
f.close()



