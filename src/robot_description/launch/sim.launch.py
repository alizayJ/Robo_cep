import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
import xacro

def generate_launch_description():
    # 1. Setup paths
    pkg_project_description = get_package_share_directory('robot_description')
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')

    # 2. Process XACRO to URDF
    xacro_file = os.path.join(pkg_project_description, 'urdf', 'rover.urdf.xacro')
    robot_description_raw = xacro.process_file(xacro_file).toxml()

    # 3. Robot State Publisher (Replaces your 'Publishing URDF' terminal command)
    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description_raw,
            'use_sim_time': True
        }]
    )

    # 4. Gazebo Sim (Replaces your 'Launch Gazebo' terminal command)
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': '-r empty.sdf'}.items(), # -r runs simulation immediately
    )

    # 5. Spawn Robot (Replaces your 'Subscribing URDF' terminal command)
    node_spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', 'robot_description', '-name', 'my_rover', '-z', '0.2'],
        output='screen',
    )

    # 6. GZ Bridge (Replaces your 'Publishing to Gazebo' terminal command)
    node_gz_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist',
            '/odom@nav_msgs/msg/Odometry@gz.msgs.Odometry',
            '/tf@tf2_msgs/msg/TFMessage@gz.msgs.Pose_V',
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock]'
        ],
        output='screen'
    )

    # 7. RViz (Added for professional visualization)
    node_rviz = Node(
        package='rviz2',
        executable='rviz2',
        output='screen',
        parameters=[{'use_sim_time': True}]
    )

    return LaunchDescription([
        node_robot_state_publisher,
        gazebo,
        node_spawn_entity,
        node_gz_bridge,
        node_rviz
    ])