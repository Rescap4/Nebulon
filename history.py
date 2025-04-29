from datetime import datetime
from sprites import *
from settings import *

class History:
    """Tracks and saves the states of all objects in the game."""
    def __init__(self):
        super().__init__()
        self.records = []  # Store game history

#    def save_state(self, objects): # method to prevent glitches
#        """Save the state of all objects only if all positions are integers."""
#        if all(obj.rect.x.is_integer() and obj.rect.y.is_integer() for obj in objects):
#            state = {
#                "object": [obj.get_state() for obj in objects]
#            }
#            self.records.append(state)
#
#            # Create a readable print statement (useless otherwise)
#            formatted_states = [
#                f"{obj.__class__.__name__.lower()}: [pos ({obj.rect.x}, {obj.rect.y}), state: {obj.state}]"
#                for obj in objects
#            ]
#            print(f"Saved: {', '.join(formatted_states)}")  # Print the formatted state
#        else: # prevent glitches
#            print("State not saved: Some object positions are not integers.")

    def save_state(self, objects):
        """Save the state of all objects."""
        #timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        state = {
            "object": [obj.get_state() for obj in objects]
        }
        self.records.append(state)

        # Create a readable print statement (useless otherwhise)
        formatted_states = [
            f"{obj.__class__.__name__.lower()}: [pos ({obj.rect.x}, {obj.rect.y}), state: {obj.state}]" #links: {self.format_links(obj.links)}]" # links recently added___
            for obj in objects
        ]
        #print(f"Saved: {', '.join(formatted_states)}")  # Print the formatted state


    def get_last_record(self):
        """Get the last saved record without removing it."""
        return self.records[-1] if self.records else None
    # else should be [-2] if player escaped

    def pop_last_record(self):
        """Remove and return the last saved record."""
        if self.records:
            return self.records.pop()
        return None
    
    #@staticmethod
    #def format_links(links):
    #    """Format the links for display."""
    #    if not links:
    #        return "None"
    #    return ", ".join([link.__class__.__name__.lower() for link in links])

