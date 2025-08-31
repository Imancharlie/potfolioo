# scripts/initialize_projects.py
import os
from django.core.files.images import ImageFile
from django.core.files import File
from potfolio_app.models import Project
from django.utils.text import slugify

def run():
    # Clear existing projects
    Project.objects.all().delete()
    
    # Create WiFile+ project
    wifile = Project(
        title="WiFile+",
        slug="wifile-plus",
        description="""
<h3>WiFile+ - Wireless File Transfer Application</h3>

        <p>WiFile+ is an innovative wireless file transfer application that allows for seamless file sharing between devices on the same network. It eliminates the need for cables, Bluetooth connections, or cloud services.</p>

        

        <h4>Key Features:</h4>

        <ul>

            <li>Fast and secure wireless file transfer</li>

            <li>Cross-platform compatibility (Windows, macOS, Linux)</li>

            <li>No size limitations for file transfers</li>

            <li>Simple and intuitive user interface</li>

            <li>No internet connection required (works on local network)</li>

            <li>End-to-end encryption for all transfers</li>

        </ul>

        

        <h4>System Requirements:</h4>

        <ul>

            <li>Any modern operating system (Windows 7+, macOS 10.12+, Ubuntu 18.04+)</li>

            <li>Minimum 2GB RAM</li>

            <li>10MB disk space</li>

            <li>Network connection (Wi-Fi or Ethernet)</li>

        </ul>

        

        <h4>Installation Instructions:</h4>

        <p>Simply download the zip file, extract it, and run the installer. The application will guide you through the setup process.</p>
        """,
        short_description="A modern wireless file transfer application for seamless sharing between devices.",
        has_download=True,
    )
    # Set download file path (assuming the file exists at the specified location)
    wifile.download_file = "downloads/Wifile.zip"
    wifile.save()
    
    # Create Caluu project
    caluu = Project(
        title="Caluu",
        slug="caluu",
        description="""
<h3>CALUU - The Ultimate GPA Calculator for University Students</h3>

<p>CALUU is a smart web-based GPA calculator designed to help university students plan their academic results,no need to enter your courses,just choose your university,college and  last program to get started. It provides real-time GPA projections, helping students plan their studies effectively.</p>

<h4>Key Features:</h4>

<ul>

    <li>Select your University/college, program, year, and semester</li>

    <li>Instant GPA calculations based on your grade entries</li>

    <li>Real-time projections to help you set academic goals</li>

    <li>Easy-to-use interface for seamless navigation</li>

    <li>Plan ahead and stay in control of your university journey</li>

</ul>

<p>Take charge of your academic success with CALUU #NoMoreSuprises. <br> Start using it today to plan and achieve your GPA goals!</p>
        """,
        short_description="Your Smart University GPA Calculator🎓📊   CALUU simplifies Academic journey by eliminating the need for tedious calculations and memorizing course codes or credits. Contains pre-filled data",
        external_url="https://caluu.pythonanywhere.com",
    )
    caluu.save()
    
    # Create Nyika Nexus project
    nyikanexus = Project(
        title="Nyika Nexus",
        slug="nyikanexus",
        description="""
<h3>Nyika Nexus - Agritech Drone Solutions & Farmer Social Platform</h3>

        <p>Nyika Nexus is an agritech solution developed by Nyika Venture Company. It utilizes drones equipped with advanced sensors to analyze soil pH levels and manage pests through targeted interventions. This technology aims to enhance agricultural efficiency and productivity.</p>

        <p>Nyika Nexus also connects farmers like a social media platform where users can post, comment, and like other peoples' posts. It includes a dedicated farmers portal for customers.</p>
        """,
        short_description="An agritech solution utilizing drone technology for fumigation, soil analysis, and a social platform for farmers.",
        external_url="https://nyikanexus.pythonanywhere.com",
    )
    nyikanexus.save()
    
    print("Projects initialized successfully!")
