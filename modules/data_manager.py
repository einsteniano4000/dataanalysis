import numpy as np

class DataManager:
    def __init__(self):
        self.series = []
        self.next_id = 1

    def add_series(self, name, x_data, y_data, x_error=None, y_error=None, color=None):
        new_series = DataSeries(self.next_id, name, x_data, y_data, x_error, y_error, color)
        self.series.append(new_series)
        self.next_id += 1
        return new_series

    def get_visible_series(self):
        return [series for series in self.series if series.visible]

    def get_all_series(self):
        return self.series

    def remove_last_series(self):
        if self.series:
            self.series.pop()
            return True
        return False

    def remove_series(self, series_id):
        for i, series in enumerate(self.series):
            if series.id == series_id:
                del self.series[i]
                return True
        return False

    def get_series_by_name(self, name):
        for series in self.series:
            if series.name == name:
                return series
        return None

    def remove_series_by_name(self, name):
        for i, series in enumerate(self.series):
            if series.name == name:
                del self.series[i]
                return True
        return False

    def clear_all_series(self):
        self.series.clear()
        self.next_id = 1

    def to_project_dict(self):
        return {
            'series': [
                {
                    'name': s.name,
                    'x_data': s.x_data.tolist(),
                    'y_data': s.y_data.tolist(),
                    'x_error': s.x_error.tolist() if s.x_error is not None else None,
                    'y_error': s.y_error.tolist() if s.y_error is not None else None,
                    'color': s.color,
                    'visible': s.visible,
                }
                for s in self.series
            ]
        }

    def load_project_dict(self, project):
        self.clear_all_series()
        for s in project.get('series', []):
            new_series = self.add_series(
                s['name'], s['x_data'], s['y_data'],
                s.get('x_error'), s.get('y_error'), s.get('color')
            )
            new_series.visible = s.get('visible', True)

class DataSeries:
    def __init__(self, id, name, x_data, y_data, x_error=None, y_error=None, color=None):
        self.id = id
        self.name = name
        self.x_data = np.array(x_data)
        self.y_data = np.array(y_data)
        self.x_error = np.array(x_error) if x_error is not None else None
        self.y_error = np.array(y_error) if y_error is not None else None
        self.color = color
        self.visible = True

    def toggle_visibility(self):
        self.visible = not self.visible

    def set_color(self, color):
        self.color = color
