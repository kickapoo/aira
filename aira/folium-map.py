import os
import folium


def generate_map(lats, lons, descprition):
    gen_map = folium.Map(location=[38, 23], zoom_start=7)
    coordinates = zip(lats, lons)
    for coord in coordinates:
        gen_map.circle_marker(list(coord),
                              popup='{}'.format(str(descprition)),
                              radius=1000,
                              line_color='#FF0000', fill_color='#FF0000')
    save_map = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                            'templates/user_map'))
    gen_map.create_map(path=save_map)
