FROM python:3
ADD solution.py /
RUN pip install requests
RUN pip install pymongo
RUN pip install flask
CMD [ "brew", "tap", "mongodb/brew"]
CMD ["brew" ,"install", "mongodb-community@5.0"]
CMD ["brew", "services" ,"start" ,"mongodb-community@5.0"]
CMD [ "python3", "./solution.py"]
