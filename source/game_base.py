from abc import ABC, abstractmethod


class GameBase(ABC):

    @abstractmethod
    def get_fields_enum(self):
        pass

    @abstractmethod
    def get_num_fields(self):
        pass

    @abstractmethod
    def get_data(self, udp_socket):
        pass

    @abstractmethod
    def get_game_state(self, receive_results, last_receive_results):
        pass

    @abstractmethod
    def get_game_state_str(self, state, last_sample, num_samples):
        pass

    @abstractmethod
    def get_car_name(self, sample):
        pass

    @abstractmethod
    def get_track_name(self, sample):
        pass

    @abstractmethod
    def get_race_duration(self, session_collection):
        pass

