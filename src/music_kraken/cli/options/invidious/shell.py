from typing import Dict, List
import requests
from dataclasses import dataclass
from collections import defaultdict

from ....utils import config, write
from ....utils import exception


INSTANCES_ENDPOINT = "https://api.invidious.io/instances.json"

@dataclass
class Instance:
    """
    Attributes which influence the quality of an instance:
    
    - users
    """
    name: str
    uri: str
    region: str
    users: int
    
    def __str__(self) -> str:
        return f"{self.name} with {self.users} users."


class InvidiousShell:
    def __init__(self):
        self.region_flags = dict()
        self.region_instances: Dict[str, List[Instance]] = defaultdict(list)
        
        self.download_instances()
        self.region = self.get_country()
        print()
        self.choose_instance()
    
    
    def process_instance(self, all_instance_data: dict):
        instance_data = all_instance_data[1]
        stats = instance_data["stats"]
        
        if not instance_data["api"]:
            return
        if instance_data["type"] != "https":
            return 
        
        region = instance_data["region"]
        flag = instance_data["flag"]
        
        self.region_flags[region] = flag
        
        instance = Instance(
            name=all_instance_data[0],
            uri=instance_data["uri"],
            region=region,
            users=stats["usage"]["users"]["total"]
        )
        
        self.region_instances[region].append(instance)
    
    def download_instances(self):
        print("Download idonvidious instances...")
        r = requests.get(INSTANCES_ENDPOINT)
        
        for instance in r.json():
            self.process_instance(all_instance_data=instance)
            
    def get_country(self):
        print("Input the country code, an example would be \"US\"")
        print(f"({' | '.join(f'{region}-{flag}' for region, flag in self.region_flags.items())})")
        
        chosen_region = ""
        
        while chosen_region.upper() not in self.region_instances:
            chosen_region = input("nearest country: ").strip().upper()
        
        return chosen_region
    
    def choose_instance(self):
        instance_list = self.region_instances[self.region]
        instance_list.sort(key=lambda x: x.users, reverse=True)
        
        # output the options
        print("Choose your instance (input needs to be a digit):")
        for i, instance in enumerate(instance_list):
            print(f"{i}) {instance}")
        
        print()
        
        # ask for index
        index = ""
        while not index.isdigit() or int(index) >= len(instance_list):
            index = input("> ").strip()
        
        instance = instance_list[int(index)]
        print()
        print(f"Setting the instance to {instance}")
        
        config.set_name_to_value("invidious_instance", instance.uri)
        write()
            