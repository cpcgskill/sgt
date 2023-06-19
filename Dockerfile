FROM python:3.10.6


WORKDIR /usr/src/app

COPY . .

#RUN pip install torch==1.13.1 torchaudio==0.13.1 torchvision==0.14.1 -i https://pypi.douban.com/simple\
#    && pip install Flask==2.2.2 -i https://pypi.douban.com/simple\
#    && pip install pymongo==4.3.3 -i https://pypi.douban.com/simple
RUN pip install -r requirements.txt -i https://pypi.douban.com/simple


EXPOSE 8000

CMD [ "python", "./main.py" ]