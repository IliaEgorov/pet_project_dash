import os

settings = {"content_img" : "golden_gate.jpg",
"style_imgs" : "starry-night.jpg",
"max_iterations" : 10
}

settings["img_name"] = settings["style_imgs"][:-4] + "_" + str(settings['max_iterations'])

neural_script_str = "python neural_style.py --content_img {content_img} --style_imgs {style_imgs} --max_size 1000 \
--max_iterations {max_iterations} --original_colors --img_name {img_name}".format(**settings)
print("----- RUN neural_style by -------")
print(neural_script_str + "\n")

os.system(neural_script_str)

