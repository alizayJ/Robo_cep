from setuptools import find_packages, setup

package_name = 'rover_rectangular'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ak',
    maintainer_email='ak@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            "Rectangular_node = rover_rectangular.rover_controller:main",
            "manipulator_node = rover_rectangular.manipulator:main",
            "rectangle_pid_tf = rover_rectangular.pid:main",
            "l_shape_node = rover_rectangular.l_shape_rover:main",
            "arm_oscillator = rover_rectangular.arm_osc:main"
        ],
    },
)
