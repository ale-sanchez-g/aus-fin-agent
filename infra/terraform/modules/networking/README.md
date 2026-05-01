# Networking Module

This module provisions the core AWS networking infrastructure for the AUS Fin Agent platform, including a VPC with public and private subnets across two availability zones, an internet gateway, a NAT gateway for private subnet egress, route tables, and security groups for the ALB, ECS API, ECS Web, and RDS services. It is designed to provide a secure, highly-available network foundation suitable for ECS Fargate workloads in the `ap-southeast-2` region.
