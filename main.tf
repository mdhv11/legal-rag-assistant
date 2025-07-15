provider "aws" {
  region = var.region
}

resource "aws_security_group" "rag_sg" {
  name        = "rag_app_sg"
  description = "Allow SSH and HTTP"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_instance" "rag_ec2" {
  ami                    = "ami-0f5ee92e2d63afc18"
  instance_type          = var.instance_type
  key_name               = var.key_name
  vpc_security_group_ids = [aws_security_group.rag_sg.id]

  root_block_device {
    volume_size           = 16
    volume_type           = "gp3"
    delete_on_termination = true
  }

  user_data = <<-EOF
              #!/bin/bash
              apt update -y
              apt install -y software-properties-common git
              add-apt-repository ppa:deadsnakes/ppa -y
              apt update
              apt install -y python3.10 python3.10-venv python3.10-dev python3-pip
              update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1
              
              cd /home/ubuntu
              git clone https://github.com/mdhv11/legal-rag.git
              cd legal-rag/app
              python3 -m venv venv
              source venv/bin/activate
              pip install --upgrade pip
              pip install -r requirements.txt
              nohup gunicorn -b 0.0.0.0:80 server:app &
              EOF


  tags = {
    Name = "RAG-Backend"
  }
}
