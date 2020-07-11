from pathlib import Path
import pandas as pd
from trajectory_utils import gps_utils as gut
from datetime import datetime

TIME_FORMAT = '%Y-%m-%d %H:%M:%S'


def geolife_trajectories_staypoint_detection(data_dir, output_dir, user_id, time_format):
    for gpsfile in data_dir.iterdir():
        if gpsfile.suffix == '.plt':
            filename = gpsfile.parts[-1]
            log = open(gpsfile, 'r')
            points = log.readlines()[6:]  # first 6 lines are useless
            data = [{'lon':i.split(',')[1], "lat":i.split(",")[0], "ts":i.split(",")[-2] + ' ' + i.split(",")[-1][:-1]} for i in points]
            df = pd.DataFrame(data)
            df['datetime'] = df.apply(lambda x: datetime.strptime(x['ts'], time_format), axis=1)
            spt = gut.extract_stay_points(df, lat_col="lat", lon_col="lon", time_col='datetime')
            if len(spt) > 3:
                spfile = output_dir.joinpath("{}_t{}.csv".format(user_id, filename[:-4]))
                data = []
                for sp in spt:
                    item = {"latitude": sp.latitude, "longitude": sp.longitude, "arrivalTime": sp.arrivTime,
                            "departTime": sp.departTime}
                    data.append(item)
                df = pd.DataFrame(data)
                df.to_csv(spfile, index=False)

def dunstan_staypoints(csv_file, output_dir, time_format='%Y-%m-%d %H:%M:%S+00:00'):
    df = pd.read_csv(csv_file)
    df['datetime'] = df.apply(lambda x: datetime.strptime(x['ts'], time_format), axis=1)
    spt = gut.extract_stay_points(df, lat_col="lat", lon_col="lon", time_col='datetime')
    spfile = output_dir.joinpath("dunstan_staypoints.csv")
    data = []
    if len(spt) > 3:
        for sp in spt:
            item = {"latitude": sp.latitude, "longitude": sp.longitude, "arrivalTime": sp.arrivTime,
                    "departTime": sp.departTime}
            data.append(item)
    df = pd.DataFrame(data)
    df.to_csv(spfile, index=False)


def main():
    base_dir = Path.cwd().parents[1]
    geolife_data_dir = base_dir.joinpath("data/Geolife_Trajectories_1.3")
    outdir = base_dir.joinpath("data", "stay-point-detection", "geolife-stay-points")
    labeled_users = pd.read_csv(geolife_data_dir.joinpath("labelled_users.csv"), dtype={'user_id': str})
    user_ids = list(labeled_users['user_id'].unique())
    dunstan_csv = base_dir.joinpath("data/dunstan_27-May-2020.csv")
    dunstan_staypoints(csv_file=dunstan_csv, output_dir=base_dir.joinpath("data"), time_format='%Y-%m-%d %H:%M:%S+00:00')

    # for user in user_ids:
    #     data = geolife_data_dir.joinpath("Data", user, 'Trajectory')
    #     geolife_trajectories_staypoint_detection(data_dir=data, output_dir=outdir, user_id=user, time_format=TIME_FORMAT)


if __name__ == '__main__':
    main()
