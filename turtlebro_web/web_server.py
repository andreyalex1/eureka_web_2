#!/usr/bin/env python3

import rclpy
import os, signal
from rclpy.node import Node
from flask import Flask, send_from_directory, send_file, request, jsonify, render_template

ROS_DOMAIN_ID :int = int(os.environ.get('ROS_DOMAIN_ID',0))
rclpy.init(domain_id=ROS_DOMAIN_ID)
ros_web_node = Node("ros_web_node")

www_path = "web"
app = Flask(__name__, static_folder='./web/static', template_folder="./web/templates")

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

def signal_handler(sig, frame):
    print('Received signal %s' % sig)
    shutdown_server()

signal.signal(signal.SIGTERM, signal_handler)

def get_video_topics(node: Node):
    
    topics = []
    for topic in node.get_topic_names_and_types():
        if topic[1] == ['sensor_msgs/msg/CompressedImage']:
          #  topics.append(topic[0].replace('/compressed',''))
            topics.append(topic[0])

    return topics        


@app.route("/")
def serve_index():
  ip_address = request.host.split(':')[0]
  return render_template('index.html', 
                        ros_host = ip_address,
                        video_topics = get_video_topics(ros_web_node))
#   return "Hello World1!"

@app.route("/<html>")
def serve_html(html):
  ip_address = request.host.split(':')[0]
  return render_template(str(html), 
                        ros_host = ip_address,
                        video_topics = get_video_topics(ros_web_node))



@app.route('/shutdown', methods=['POST'])
def shutdown():
    shutdown_server()
    return 'Server shutting down...'

def main():
  app.run(host="0.0.0.0", port=8080, threaded=True, debug=False)

if __name__ == "__main__":
  main()