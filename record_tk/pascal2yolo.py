import os
import xml.etree.ElementTree as ET


def convert_voc_to_yolo(voc_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for xml_file in os.listdir(voc_folder):
        if xml_file.endswith('.xml'):
            tree = ET.parse(os.path.join(voc_folder, xml_file))
            root = tree.getroot()

            yolo_file = os.path.splitext(xml_file)[0] + '.txt'
            yolo_path = os.path.join(output_folder, yolo_file)

            with open(yolo_path, 'w') as f:
                for obj in root.findall('object'):
                    cls = obj.find('name').text
                    bbox = obj.find('bndbox')
                    x_center = (float(bbox.find('xmin').text) + float(bbox.find('xmax').text)) / 2
                    y_center = (float(bbox.find('ymin').text) + float(bbox.find('ymax').text)) / 2
                    width = float(bbox.find('xmax').text) - float(bbox.find('xmin').text)
                    height = float(bbox.find('ymax').text) - float(bbox.find('ymin').text)

                    yolo_line = f"{cls} {x_center} {y_center} {width} {height}\n"
                    f.write(yolo_line)


voc_folder = r'E:\Codes\PyProjects\yolo8_dxc\datasets\fortestmy\labels\train'
output_folder = r'E:\Codes\PyProjects\yolo8_dxc\datasets\fortestmy\labels\train'
convert_voc_to_yolo(voc_folder, output_folder)
