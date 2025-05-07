FILE_PATH="./custom_detectors/events"
DETECTOR="SK_DC" SIGNAL_FILE="${FILE_PATH}/SK-Gd_ibd-dc_NH.txt" snap_run sn_client.yml &
DETECTOR="SK_n" SIGNAL_FILE="${FILE_PATH}/SK-Gd_ibd-n_NH.txt" snap_run sn_client.yml &
DETECTOR="KamLAND" SIGNAL_FILE="${FILE_PATH}/KamLAND_ibd_NH.txt" snap_run sn_client.yml &
DETECTOR="Borexino" SIGNAL_FILE="${FILE_PATH}/Borexino_ibd_NH.txt" snap_run sn_client.yml &

wait -n
