import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.actions import ExecuteProcess
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution

from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

urdf_filename = 'kr210.urdf.xml'

def generate_launch_description():
    package_share_dir = get_package_share_directory("kr210_arm")
    urdf_file = os.path.join(package_share_dir, "urdf", "kr210.urdf")

    robot_urdf = os.path.join(package_share_dir, "urdf", urdf_filename)
        
    with open(robot_urdf, 'r') as infp:
        robot_desc = infp.read()

    
    
    controller_file = os.path.join(package_share_dir, "config", "config_file.yaml")
    robot_description = {"robot_description": robot_desc}

    gazebo_server = IncludeLaunchDescription(
                            PythonLaunchDescriptionSource([
                                PathJoinSubstitution([
                                    FindPackageShare('gazebo_ros'),
                                                     'launch',
                                                     'gzserver.launch.py'])
                                 ]),
                                launch_arguments={'pause': 'true'}.items())

    gazebo_client = IncludeLaunchDescription(
                            PythonLaunchDescriptionSource([
                                PathJoinSubstitution([
                                    FindPackageShare('gazebo_ros'),
                                                     'launch',
                                                     'gzclient.launch.py'])
                                ]) )
    
    joint_state_broadcaster_controller_node =  ExecuteProcess(
                                                    cmd=['ros2', 'control', 'load_controller', '--set-state', 'active',
                                                        'joint_state_broadcaster'],
                                                    output='screen'
                                                )

    joint_trajectory_controller_node = ExecuteProcess(
                                            cmd=['ros2', 'control', 'load_controller', '--set-state', 'active',
                                                'joint_trajectory_controller'],
                                                    output='screen'
                                        )
    
    return LaunchDescription(
        [
            gazebo_server, 
            gazebo_client,

            # urdf spawn node
            Node(
                package="gazebo_ros",
                executable="spawn_entity.py",
                arguments=["-entity", "kr210_arm", '-file', urdf_file],
                output = 'screen',
            ),

            Node(
                package="robot_state_publisher",
                executable="robot_state_publisher",
                name='robot_state_publisher',
                parameters=[robot_description],
                output = 'screen'
            ),
            
            Node(
                package="controller_manager",
                executable="ros2_control_node",
                parameters=[robot_description, controller_file],
                output={
                    "stdout": "screen",
                    "stderr": "screen",
                },
            ),

            #joint_state_broadcaster_controller_node,
            Node(
                package="controller_manager",
                executable="spawner",
                arguments=["joint_state_broadcaster", "--controller-manager", "/controller_manager"],
            ),

            #joint_trajectory_controller_node,
            Node(
                package="controller_manager",
                executable="spawner",
                arguments=["joint_trajectory_controller", "-c", "/controller_manager"],
            )
        ]
    )