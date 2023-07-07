import obswebsocket
from obswebsocket import obsws
import math
import time
import os

OBS_PASSWORD = os.getenv("OBS_PASSWORD")

class OBSWebsocketsManager():
    def __init__(self) -> None:
        self.ws = obsws("localhost", 4455, OBS_PASSWORD)
        self.ws.connect()
    
    def get_item_id(self, scene_name, element_name):
        response = self.ws.call(obswebsocket.requests.GetSceneItemList(sceneName=scene_name))
        
        items = response.getSceneItems()

        scene_item_id = None
        for item in items:
            if item['sourceName'] == element_name:
                scene_item_id = item['sceneItemId']
                break

        if scene_item_id:
            return scene_item_id
        else:
            return "F"

    def set_source_visibility(self, scene_name, element_name, set):

        scene_item_id = self.get_item_id(scene_name, element_name)

        transform_data = {
            "sceneName": scene_name,
            "sceneItemId": scene_item_id,
            "sceneItemEnabled": set
        }
        
        set_transform_request = obswebsocket.requests.SetSceneItemEnabled(**transform_data)
        self.ws.call(set_transform_request)

    def shake(self, scene_name, element_name, rot):
        scene_item_id = self.get_item_id(scene_name, element_name)

        transform_data = {
            "sceneName": scene_name,
            "sceneItemId": scene_item_id,
            "sceneItemTransform": {
                "rotation": rot
            }
        }

        set_transform_request = obswebsocket.requests.SetSceneItemTransform(**transform_data)
        self.ws.call(set_transform_request)

    def source_checker(self, scene_name):
        response = self.ws.call(obswebsocket.requests.GetSceneItemList(sceneName=scene_name))
        print(response)
        return response

def main():
    scene_name = "ingame"
    element_name = "CultistGary"
    obs_websocketmanager = OBSWebsocketsManager()
    # print(obs_websocketmanager.source_checker("ingame"))
    print(obs_websocketmanager.get_item_id(scene_name, element_name))
    start_time = time.time()
    rot = 0
    while time.time() < (start_time + 5):
        rot = 10*math.sin(12*time.time())
        obs_websocketmanager.shake(scene_name, element_name, rot)
    rot = 0
    obs_websocketmanager.shake(scene_name, element_name, rot)
    

if __name__ == "__main__":
    main()