"""
Company: Somikoron AI
Property: This API is the proprietary property of Somikoron AI.

Description: 
This client-side API is designed to enhance image and video processing by detecting defects in visual content.
It accepts images and videos as input, analyzes them using advanced algorithms, and returns results indicating
any defects identified during the processing.The API efficiently draws bounding boxes around detected defects,
providing clear visual feedback.

Key Features:
- Supports both image and video inputs.
- Utilizes state-of-the-art machine learning techniques for accurate defect detection.
- Returns processed images with bounding boxes around detected defects for easy visualization.
- Streamlined for quick integration into client applications.

Usage: Ideal for industries such as manufacturing, quality control, and inspection, where monitoring visual content for defects is critical.
"""



from collections import defaultdict
import json
import mimetypes
import os
import pickle
import requests
from PIL import Image
import io
import cv2
import random
import numpy as np
# from cryptography.fernet import Fernet


class Retrofit:
    def __init__(self, url="https://api.somikoron.ai/api/", auth_key="", auth_pass="",
                  font_size=7, font_thickness=3, line_space=10, detect_mode="all", label_mode="all"):
        self.url = url
        self.auth_key = auth_key
        self.auth_pass = auth_pass
        self.credential = {"auth_key":auth_key, 'auth_pass':auth_pass}
        self.font_size = font_size
        self.font_thickness = font_thickness
        self.line_space = line_space
        self.detect_mode = detect_mode
        self.label_mode = label_mode


        self.label_map = {
            "Corrosion": ["Corrosion_Ct", "Corrosion_Dt"],
            "Crack": ["Crack_Ct", "Crack_Dt"],
            "Abnormal Spacing": ["Abnormal Spacing_Ct", "Abnormal Spacing_Bt"],
            "Functional Disorder of Bearing": ["Functional Disorder of Bearing_Ct", "Functional Disorder of Bearing_Bt"],
            "Spalling/Exposed Rebar": ["Spalling/Exposed Rebar_Ct", "Spalling/Exposed Rebar_Bt"]
        }


    

    def get_video_data_sample(self, file_path, save=False, sample=3, output="output/", temp="temp/"):
        if not os.path.exists(temp):
            os.makedirs(temp)  # Create the temp directory if it doesn't exist

        if not os.path.exists(output):
            os.makedirs(output)  # Create the output directory if it doesn't exist

        result_data = []
        frame_names = []
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"The file '{file_path}' does not exist.")
        
        if not self._is_video_file(file_path):
            raise ValueError(f"The file '{file_path}' is not a valid video file.")

        try:
            cap = cv2.VideoCapture(file_path)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            output_video_path = f'{output}{os.path.basename(file_path)}'   
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_video_path, fourcc, fps, (frame_width, frame_height))  
            
            # Select 3 random frames to process
            random_frames = random.sample(range(1, total_frames + 1), sample)

            i = 1
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break  # End of video

                # Only process if the frame number is in the selected random frames
                if i in random_frames:
                    _, encoded_image = cv2.imencode('.jpg', frame)
                    image_buffer = io.BytesIO(encoded_image.tobytes())
                    buffered_reader = io.BufferedReader(image_buffer)
                    files = {'file': buffered_reader}
                    response = requests.post(self.url, data=self.credential, files=files)
                    
                    if response.status_code == 200:
                        if 'application/json' in response.headers.get('Content-Type', ''):
                            data = json.loads(response.text)
                            result_data.append(data['results'])
                        if save:
                            cv2.imwrite(f'{temp}frame{i}.jpg', frame)
                            frame_names.append(f'{temp}frame{i}.jpg')
                            print(f'Processed Frame {i}')  # Show frame progress   
                i += 1
            if save:
                for frame, result in zip(frame_names, result_data):
                    c_frame = self._img_data(result[0], result[1], frame)
                    c_frame_np = np.array(c_frame)
                    c_frame_bgr = cv2.cvtColor(c_frame_np, cv2.COLOR_RGB2BGR)
                    output_image_path = f'{output}frame{random_frames[frame_names.index(frame)]}.jpg'
                    cv2.imwrite(output_image_path, c_frame_bgr)  # Save in the output folder
                    print(f'\nSaved: {output_image_path}')
                    if os.path.exists(frame):
                        os.remove(frame)
            cap.release()
            out.release()

            if self.detect_mode == 'all':
                return result_data
            elif self.detect_mode == 'rating':
                result = []
                for r in result_data:
                    result.append(r[1])
                return result
            elif self.detect_mode == 'defect':
                result = []
                for r in result_data:
                    result.append(r[0])
                return result
            else:
                print("someting went wrong")
        except Exception as e:
            raise Exception(f"An unexpected error occurred: {e}")
        


    def get_video_data(self, file_path, save=False, output="output/", temp="temp/"):
        if not os.path.exists(temp):
            os.makedirs(temp)  # Create the temp directory if it doesn't exist
        if not os.path.exists(output):
            os.makedirs(output)  # Create the temp directory if it doesn't exist

        result_data = []
        frame_names = []
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"The file '{file_path}' does not exist.")
        
        if not self._is_video_file(file_path):
            raise ValueError(f"The file '{file_path}' is not a valid video file.")
        try:
            cap = cv2.VideoCapture(file_path)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            output_video_path = f'{output}{os.path.basename(file_path)}'   
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_video_path, fourcc, fps, (frame_width, frame_height))  
            i =1
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break  # End of video
                _, encoded_image = cv2.imencode('.jpg', frame)
                image_buffer = io.BytesIO(encoded_image.tobytes())
                buffered_reader = io.BufferedReader(image_buffer)
                files = {'file': buffered_reader}
                response = requests.post(self.url, data=self.credential, files=files)
                if response.status_code == 200:
                    if 'application/json' in response.headers.get('Content-Type', ''):
                        data = json.loads(response.text)
                        result_data.append(data['results'])
                    if save:
                        cv2.imwrite(f'{temp}frame{i}.jpg', frame)
                        frame_names.append(f'{temp}frame{i}.jpg')
                        percentage_complete = (i) / total_frames * 100
                        # Print the percentage of processing complete
                        print(f'\rProcessing: {percentage_complete:.2f}%', end='')  # Print on the same line
                        i += 1
            if save:
                i = 1
                for frame, result in zip(frame_names, result_data):
                    c_frame = self._img_data(result[0],result[1], frame)
                    c_frame_np = np.array(c_frame)
                    c_frame_bgr = cv2.cvtColor(c_frame_np, cv2.COLOR_RGB2BGR)
                    percentage_written = (i) / total_frames * 100
                    print(f'\r Frame Writing: {percentage_written:.2f}%', end='')  # Print on the same line
                    out.write(c_frame_bgr)    
                    i += 1
                    if os.path.exists(frame):
                        os.remove(frame)
            cap.release()
            out.release()
            print()
            if self.detect_mode == 'all':
                return result_data
            elif self.detect_mode == 'rating':
                result = []
                for r in result_data:
                    result.append(r[1])
                return result
            elif self.detect_mode == 'defect':
                result = []
                for r in result_data:
                    result.append(r[0])
                return result
            else:
                print("someting went wrong")
            # return result_data
        except requests.exceptions.RequestException as e:
            raise Exception(f"An error occurred during the request: {e}")
        except pickle.UnpicklingError as e:
            raise Exception(f"Failed to unpickle response data: {e}")
        except Exception as e:
            raise Exception(f"An unexpected error occurred: {e}")



    def get_image_data(self, file_path, save=False, output="output/"):
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"The file '{file_path}' does not exist.")
        if not self._is_image_file(file_path):
            raise ValueError(f"The file '{file_path}' is not a valid image file.")
        if not os.path.exists(output):
            os.makedirs(output)
        try:
            with open(file_path, 'rb') as f:
                files = {'file': f}
                # print(files)
                response = requests.post(self.url, data=self.credential, files=files)
            # Verify if the response is valid before attempting to unpickle
            if response.status_code == 200:
                if 'application/json' in response.headers.get('Content-Type', ''):
                    data = json.loads(response.text)
                    results = data['results']
                else:
                    raise ValueError("Unexpected response format.")
                if save:
                    image = self._img_data(results[0], results[1], file_path)
                    image = np.array(image)
                    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                    # Save the output image
                    if output:
                        if not os.path.exists(output):
                            os.makedirs(output)
                        cv2.imwrite(f'{output}/{os.path.basename(file_path)}', image)
                
                if self.detect_mode == 'all':
                    return results
                elif self.detect_mode == 'rating':
                    return results[1]
                elif self.detect_mode == 'defect':
                    return [results[0]]
                else:
                    print("someting went wrong")
            else:
                raise Exception(f"Failed to get a valid response. Status code: {response.status_code}, Response: {response.text}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"An error occurred during the request: {e}")
        except pickle.UnpicklingError as e:
            raise Exception(f"Failed to unpickle response data: {e}")
        except Exception as e:
            raise Exception(f"An unexpected error occurred: {e}")
        

    def _img_data(self, defect_results, rating_results, file_path):
        if isinstance(file_path, str):
            frame = cv2.imread(file_path)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        elif isinstance(file_path, np.ndarray):
            frame = file_path
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        else:
            raise ValueError("Invalid input: must be a file path (str) or an image (ndarray)")

        if defect_results is None or rating_results is None:
            print("Error: results are None")
            return

        defect_colors = {
            0: (255, 0, 0),      # Corrosion: Red
            1: (0, 255, 0),      # Crack: Green
            2: (0, 0, 255),      # Abnormal Spacing: Blue
            3: (255, 165, 0),    # Functional Disorder of Bearing: Orange
            4: (128, 0, 128),    # Spalling/Exposed Rebar: Purple
        }

        rating_colors = {
            0: (95, 15, 64),     # Corrosion_Dt: Dark Magenta (#5F0F40)
            1: (0, 255, 255),    # Crack_Ct: Cyan (#00FFFF)
            2: (0, 255, 255),    # Abnormal Spacing_Ct: Cyan (#00FFFF)
            3: (0, 255, 255),    # Functional Disorder of Bearing_Ct: Cyan (#00FFFF)
            4: (0, 255, 255),    # Spalling/Exposed Rebar_Ct: Cyan (#00FFFF)
            5: (0, 255, 255),    # Corrosion_Ct: Cyan (#00FFFF)
            6: (95, 15, 64),     # Crack_Dt: Dark Magenta (#5F0F40)
            7: (255, 255, 255),  # Abnormal Spacing_Bt: White (#FFFFFF)
            8: (255, 255, 255),  # Functional Disorder of Bearing_Bt: White (#FFFFFF)
            9: (255, 255, 255),  # Spalling/Exposed Rebar_Bt: White (#FFFFFF)
        }


        # Unique color assignment to ensure no duplicates
        assigned_colors = {}

        # Assign colors to each defect class
        for item in defect_results['data']:
            cls = item['box_cls']
            if cls not in assigned_colors:
                assigned_colors[cls] = defect_colors.get(cls)  # Use defect colors (0-4)

        # Assign colors to each rating class
        for item in rating_results['data']:
            cls = item['box_cls']
            if cls not in assigned_colors:
                assigned_colors[cls] = rating_colors.get(cls)  # Use rating colors (0-9)

        # Get the dynamic image dimensions from the current frame
        height, width, _ = frame.shape

        # Calculate font size relative to the frame dimensions (proportional scaling)
        font_scale = height / (70 * max(1, int(20 - self.font_size)))
        font_thickness = self.font_thickness
        # font_thickness = int(height / (40 * max(1, int(20 - self.font_size))))


        if self.detect_mode == "all":
            # Bounding box drawing for defect and rating
            for item in defect_results['data']:
                box_xyxy = item['box_xyxy']
                cls = item['box_cls']
                x1, y1, x2, y2 = map(int, box_xyxy)

                box_width = x2 - x1
                box_height = y2 - y1
                box_scale = max(2, int(min(box_width, box_height) / 40))

                color = defect_colors.get(cls)  # Use defect colors (0-4)
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, box_scale)

            for item in rating_results['data']:
                box_xyxy = item['box_xyxy']
                cls = item['box_cls']
                x1, y1, x2, y2 = map(int, box_xyxy)

                box_width = x2 - x1
                box_height = y2 - y1
                box_scale = max(2, int(min(box_width, box_height) / 45))

                color = rating_colors.get(cls)  # Use rating colors (0-9)
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, box_scale)
        elif self.detect_mode == "defect":
            for item in defect_results['data']:
                box_xyxy = item['box_xyxy']
                cls = item['box_cls']
                x1, y1, x2, y2 = map(int, box_xyxy)

                box_width = x2 - x1
                box_height = y2 - y1
                box_scale = max(2, int(min(box_width, box_height) / 40))

                color = defect_colors.get(cls)  # Use defect colors (0-4)
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, box_scale)
        elif self.detect_mode == 'rating':
            for item in rating_results['data']:
                box_xyxy = item['box_xyxy']
                cls = item['box_cls']
                x1, y1, x2, y2 = map(int, box_xyxy)

                box_width = x2 - x1
                box_height = y2 - y1
                box_scale = max(2, int(min(box_width, box_height) / 45))

                color = rating_colors.get(cls)  # Use rating colors (0-9)
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, box_scale)
        else:
            raise ValueError(f"Invalid mode: '{self.detect_mode}' not found. Please choose 'all' or 'defect' or 'rating'.")

        # Label preparation (defects and ratings)
        reverse_defect_cls = {value: key for key, value in defect_results['cls'].items()}
        reverse_rating_cls = {value: key for key, value in rating_results['cls'].items()}
        
        reverse_label_map = {v: k for k, values in self.label_map.items() for v in values}
        combine_set = {}

        for defect in defect_results['data']:
            box_cls = defect['box_cls']
            defect_cls = defect_results['cls'].get(str(box_cls))
            if box_cls not in combine_set:
                combine_set[box_cls] = [{defect_cls : "defect"}]  # Initialize with defect class
        rating_box_classes = {rating['box_cls'] for rating in rating_results['data']}

        for box in rating_box_classes:
            get_r_cls = rating_results['cls'].get(str(box))
            for key, value in combine_set.items():
                v = list(value[0].keys())[0]
                if reverse_label_map.get(get_r_cls) in value[0].keys():
                    combine_set[key].append({get_r_cls:'rating'})
        
        # rating_short = {
        #     'Corrosion_Dt': 'Dt',
        #     'Crack_Ct': 'Ct',
        #     'Abnormal Spacing_Ct': 'Ct',
        #     'Functional Disorder of Bearing_Ct': 'Ct',
        #     'Spalling/Exposed Rebar_Ct': 'Ct',
        #     'Corrosion_Ct': 'Ct',
        #     'Crack_Dt': 'Dt',
        #     'Abnormal Spacing_Bt': 'Bt',
        #     'Functional Disorder of Bearing_Bt': 'Bt',
        #     'Spalling/Exposed Rebar_Bt': 'Bt'
        # }
        # for key, value in rating_results['cls'].items():
        #     print(rating_short.get(value))

        set_dict = defaultdict(set)
        # Iterate over the dictionary to fill the sets
        for key, value_list in combine_set.items():
            for value in value_list:
                for k, v in value.items():
                    set_dict[key].add((k, v))

        # Convert back to a regular dictionary
        set_dict = dict(set_dict)
        for key, value in set_dict.items():
            set_dict[key] = sorted(value, key=lambda x: x[1] != 'defect')
        
        
        # filter, only rating
         
        # filter, only defect
        

        if self.label_mode == 'defect':
            set_dict = {key: {item for item in value if item[1] == 'defect'} for key, value in set_dict.items()}
        elif self.label_mode == 'rating':
            set_dict = {key: {item for item in value if item[1] == 'rating'} for key, value in set_dict.items()}
        elif self.label_mode == 'all':
            pass
        else:
            raise ValueError(f"Invalid mode: '{self.label_mode}' not found. Please choose 'all' or 'defect', 'rating'.")

        # Assume these are already defined earlier in the code with the respective colors:
        # defect_colors: for defect class colors (5 colors)
        # rating_colors: for rating class colors (10 colors)

        max_label_width = 0
        label_strings = []

        # Iterate over the set_dict to process defect and rating labels
        for color_key, value_set in set_dict.items():
            # Combine defect and rating labels as a single string for each key
            combined_label = " ".join([item[0] for item in value_set])  # Extract only the label part from each tuple
            label_strings.append(combined_label)
            # Measure the width of the combined label
            (text_width, _), _ = cv2.getTextSize(combined_label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_thickness)
            max_label_width = max(max_label_width, text_width)

        start_x, start_y = width - max_label_width - 30, 30  # Adjust for right alignment

        # Draw the labels with their corresponding colors
        for color_key, value_set in set_dict.items():
            label_x = start_x + 10
            total_text_height = 0
            # Iterate through the set of defect and rating tuples
            for label, class_type in value_set:
                # Determine if the label is for defect or rating and set the corresponding color
                if class_type == 'defect':  # For defect class
                    color = defect_colors.get(int(reverse_defect_cls.get(label)))  # Default to white if no color
                    # print(color)
                else:  # For rating class
                    color = rating_colors.get(int(reverse_rating_cls.get(label)))  # Default to white if no color

                # Get the size of the current text (label)
                (text_width, text_height), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_thickness)

                # Ensure label stays within image bounds
                if start_y + text_height + 10 > height:
                    break  # Stop if we're going beyond the image height

                # Draw the label text with the corresponding color
                cv2.putText(frame, label, (label_x, start_y + text_height), cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, font_thickness)

                # Update the x-coordinate for the next part (spacing between defect and rating labels)
                label_x += text_width + 10  # Adding 10 for a slight gap between defect and rating labels
                total_text_height = text_height

            # Move the y-coordinate down for the next label
            start_y += total_text_height + self.line_space  # Line spacing after each full label



        # rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(frame)
        return image
    

    # Verify if it's an image or not
    def _is_image_file(self, file_path):
        try:
            # Try to open the image with Pillow
            with Image.open(file_path) as img:
                img.verify()  # Verify that this is indeed an image
            return True
        except (IOError, SyntaxError) as e:
            return False
    
    # Verify if it's a video file
    def _is_video_file(self, file_path):
        # Guess the file type based on its extension
        file_type, _ = mimetypes.guess_type(file_path)
        
        # Supported video formats
        video_formats = ['video/mp4', 'video/mpeg', 'video/avi', 'video/mov', 'video/mkv']
        
        if file_type in video_formats:
            return True
        else:
            return False