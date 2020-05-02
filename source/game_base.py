from abc import ABC, abstractmethod


class GameBase(ABC):

    @staticmethod
    @abstractmethod
    def get_valid_game_names() -> list:
        pass

    @abstractmethod
    def load_data(self, file_path):
        pass

    @abstractmethod
    def save_data(self, data, file_path):
        pass

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

    @abstractmethod
    def get_progress(self, session_collection):
        pass

    @abstractmethod
    def get_plot_data(self, session_collection):
        pass
