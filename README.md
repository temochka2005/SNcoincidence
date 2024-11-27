# SNcoincidence

### Installation:
```shell
git clone https://github.com/temochka2005/SNcoincidence.git
cd SNcoincidence
pip install -r requirements.txt
```

### How to run:

#### Clients

Running clients with their username and shift(mean value for normal distribution). 
```shell
USER=user1 shift=5.0 snap_run example.yml
```
It's possible to run several clients in separate terminals.

#### Server

Start server in separate terminal:
```shell
snap_run example.yml -n node_server
```