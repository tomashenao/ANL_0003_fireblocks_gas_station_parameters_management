# ANL_0003_fireblocks_gas_station_parameters_management
This repository contains the code that directly configures the parameters of Fireblocks Gas Station. It basically focuses on three main parameters:

1) Minimum threshold: triggers the Gas Station to auto-fuel once the EVM compatible currency balance is below a certain threshold.
2) Fueling amount: it is the amount that will fuel the Gas Station once the alert is triggered.
3) Max Gwei: for the transaction to be correctly executed, price of Gwei should be below this value.
