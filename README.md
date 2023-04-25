# mempool-checker

mempool-checker allows you to compare mempools of different RPC nodes (public/private) and see the difference in how many transactions they have. this can help you optimize your peers for the best mempool saturation.

## how to use

```bash
pip install -r requirements.txt
python3 main.py --rpcs https://evmos-rpc.polkachu.com --rpcs https://evmos-rpc.stakely.io
```