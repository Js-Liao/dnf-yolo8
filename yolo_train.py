if __name__ == '__main__':
    from ultralytics import YOLO

    yaml_file = r"datasets\dxcjus\dxc.yaml"

    model = YOLO("yolov8n.pt")
    model.train(data=yaml_file, batch=-1, epochs=350, verbose=True)
