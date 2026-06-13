import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
import xacro
from launch.actions import ExecuteProcess


def generate_launch_description():

    pkg_description = get_package_share_directory('robot_description')
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')

    # Process Xacro files
    rover_xml = xacro.process_file(
        os.path.join(pkg_description, 'urdf', 'rover.urdf.xacro')
    ).toxml()

    arm_xml = xacro.process_file(
        os.path.join(pkg_description, 'urdf', 'manipulator.urdf.xacro')
    ).toxml()

    # Gazebo
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')]
        ),
        launch_arguments={'gz_args': '-r empty.sdf'}.items(),
    )
    # Reset World
    reset_world = ExecuteProcess(
    cmd=[
        'ros2', 'service', 'call',
        '/world/empty/control',
        'gz_msgs/srv/WorldControl',
        '{reset: {all: true}}'
    ],
    output='screen'
     )
    # Spawn Rover
    spawn_rover = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-string', rover_xml,
            '-name', 'my_rover',
            '-x', '0.0',
            '-y', '-2.0',
            '-z', '0.1'
        ],
        output='screen'
    )

    # Spawn Manipulator
    spawn_arm = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-string', arm_xml,
            '-name', 'manipulator',
            '-x', '-1.5',
            '-y', '0.0',
            '-z', '0.1'
        ],
        output='screen'
    )
    
    # Bridge
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[

            # Rover
            '/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist',
            '/model/my_rover/odometry@nav_msgs/msg/Odometry@gz.msgs.Odometry',

            # Manipulator joints
            '/model/manipulator/joint/joint_1/cmd_pos@std_msgs/msg/Float64@gz.msgs.Double',
            '/model/manipulator/joint/joint_2/cmd_pos@std_msgs/msg/Float64@gz.msgs.Double',

            # Sensor
            '/arm/scan@sensor_msgs/msg/LaserScan@gz.msgs.LaserScan',

            # Clock
            '/clock@rosgraph_msgs/msg/Clock@gz.msgs.Clock',
        ],
        remappings=[
            ('/model/my_rover/odometry', '/odom'),
        ],
        output='screen'
    )

    # Manipulator Control Node
    manipulator_node = Node(
        package='rover_rectangular',
        executable='manipulator_node',
        name='manipulator_node',
        output='screen'
    )

    # Rover Motion Node
    rectangular_node = Node(
        package='rover_rectangular',
        executable='Rectangular_node',
        name='rectangular_node',
        output='screen'
    )

    return LaunchDescription([
        gazebo,
        reset_world,
        spawn_rover,
        spawn_arm,
        bridge,
        manipulator_node,
        rectangular_node
    ]) 