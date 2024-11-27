# SNcoincidence

### Installation:
```shell
git clone https://github.com/temochka2005/SNcoincidence.git
cd SNcoincidence
pip install -r requirements.txt
```

### How to run:

#### Clients

Running clients with their detector. 
```shell
DETECTOR=detector1 snap_run sn_client.yml
```
It's possible to run several clients in separate terminals.

#### Server

Start server in separate terminal:
```shell
snap_run example.yml
```