import pandas as pd
import geopandas as gpd
from shapely.geometry import LineString
import argparse
import os


def read_track_data(data_folder, datset_id):
    """
    Read track data from a CSV file.
    
    Args:
        data_folder (str): Path to the folder containing dataset folders
        datset_id (str): Dataset ID
        
    Returns:
        pd.DataFrame: Track data with columns ['lon', 'lat', 'track_id']
    """
    track_data = pd.read_csv(f'{data_folder}/{datset_id}/{datset_id}.track', 
                            sep=r'\s+', header=None)
    
    track_data.columns = ['lon', 'lat', 'track_id']
    track_data['track_id'] = track_data['track_id'].astype(int)
    
    return track_data


def read_nodes_data(data_folder, datset_id):
    """
    Read nodes data from a CSV file.
    
    Args:
        data_folder (str): Path to the folder containing dataset folders
        datset_id (str): Dataset ID
        
    Returns:
        pd.DataFrame: Nodes data with columns ['lon', 'lat', 'node_id']
    """
    nodes_data = pd.read_csv(f'{data_folder}/{datset_id}/{datset_id}.nodes', 
                            sep=r'\s+', header=None)
    
    nodes_data.columns = ['lon', 'lat']
    nodes_data['node_id'] = nodes_data.index
    
    return nodes_data


def read_arcs_data(data_folder, datset_id):
    """
    Read arcs data from a CSV file.
    
    Args:
        data_folder (str): Path to the folder containing dataset folders
        datset_id (str): Dataset ID
        
    Returns:
        pd.DataFrame: Arcs data with columns ['node_id_start', 'node_id_end', 'arc_id']
    """
    arcs_data = pd.read_csv(f'{data_folder}/{datset_id}/{datset_id}.arcs', 
                            sep=r'\s+', header=None)
    
    arcs_data.columns = ['node_id_start', 'node_id_end']
    arcs_data['arc_id'] = arcs_data.index
    
    return arcs_data


def read_route_data(data_folder, datset_id):
    """
    Read route data from a CSV file.
    
    Args:
        data_folder (str): Path to the folder containing dataset folders
        datset_id (str): Dataset ID
        
    Returns:
        pd.DataFrame: Route data with column ['arc_id']
    """
    route_data = pd.read_csv(f'{data_folder}/{datset_id}/{datset_id}.route', 
                            sep=r'\s+', header=None)
    
    route_data.columns = ['arc_id']
    route_data['arc_id'] = route_data['arc_id'].astype(int)
    
    return route_data


def create_line(row):
    """
    Create a LineString geometry from start and end coordinates.
    
    Args:
        row (pd.Series): Row containing 'lon_start', 'lat_start', 'lon_end', 'lat_end'
        
    Returns:
        LineString: Geometry representing the line segment
    """
    return LineString([(row['lon_start'], row['lat_start']), 
                       (row['lon_end'], row['lat_end'])])


def save_output(output_folder, dataset_id, gdf, type_df):
    """
    Save GeoDataFrame to a GeoPackage file.
    
    Args:
        output_folder (str): Output folder path
        dataset_id (str): Dataset ID
        gdf (gpd.GeoDataFrame): GeoDataFrame to save
        type_df (str): Type of data (e.g., 'road_graph', 'track')
    """
    os.makedirs(f'{output_folder}/{dataset_id}', exist_ok=True)
    output_path = f'{output_folder}/{dataset_id}/{dataset_id}_{type_df}.gpkg'
    gdf.to_file(output_path, driver='GPKG')
    print(f"{type_df.capitalize()} saved to {output_path}")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Process dataset")
    parser.add_argument(
        "--dataset-id",
        type=str,
        default="00000000",
        help="Dataset ID to process"
    )
    args = parser.parse_args()

    data_folder = 'src/read_impoted_dataset/map-matching-dataset'
    dataset_id = args.dataset_id

    output_folder = 'src/read_impoted_dataset/output_files'

    print(f"Dataset ID: {dataset_id}")

    track_data = read_track_data(data_folder, dataset_id)

    nodes_data = read_nodes_data(data_folder, dataset_id)

    arcs_data = read_arcs_data(data_folder, dataset_id)

    route_data = read_route_data(data_folder, dataset_id)

    print(track_data.head())
    print(nodes_data.head())
    print(arcs_data.head())
    print(route_data.head())

    print(f"Track data length: {len(track_data)}")      
    print(f"Nodes data length: {len(nodes_data)}")
    print(f"Arcs data length: {len(arcs_data)}")
    print(f"Route data length: {len(route_data)}")


    # 1. Attach coordinates for START (node_id_start)
    road_graph = pd.merge(
        arcs_data, 
        nodes_data, 
        left_on='node_id_start', 
        right_on='node_id', 
        how='left'
    ).rename(columns={'lat': 'lat_start', 'lon': 'lon_start'})

    # Remove unnecessary node_id column after first join
    road_graph = road_graph.drop(columns=['node_id'])

    # 2. Attach coordinates for END (node_id_end)
    road_graph = pd.merge(
        road_graph, 
        nodes_data, 
        left_on='node_id_end', 
        right_on='node_id', 
        how='left'
    ).rename(columns={'lat': 'lat_end', 'lon': 'lon_end'})

    # Remove unnecessary node_id column again
    road_graph = road_graph.drop(columns=['node_id'])

    print(road_graph.head())


    # Create geometry
    road_graph['geometry'] = road_graph.apply(create_line, axis=1)

    road_graph = road_graph.merge(
        route_data[['arc_id']].assign(is_route=True),
        on='arc_id',
        how='left'
    ).fillna({'is_route': False})

    print(road_graph.head())

    # Convert to GeoDataFrame
    gdf_road_graph = gpd.GeoDataFrame(road_graph, geometry='geometry', crs="EPSG:4326")

    save_output(output_folder, dataset_id, gdf_road_graph, 'road_graph')


    #####################

    # Create GeoDataFrame for track data
    gdf_track = gpd.GeoDataFrame(
        track_data,
        geometry=gpd.points_from_xy(track_data['lon'], track_data['lat']),
        crs="EPSG:4326"
    )

    save_output(output_folder, dataset_id, gdf_track, 'track')