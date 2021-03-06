#!/usr/bin/env python
from flask import render_template, flash, redirect, url_for, request
from subprocess import check_call, Popen, call
import re, os, sys

from app import app
from app import db
from app.spider.spider import spider_func
from app.spider.sprank import sprank_func
from app.spider.spjson import spjson_func
from app.spider.compute_embeddings import compute_embeddings
from app.spider.process_viz import get_viz

@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            web_url = request.form["webUrl"]
            num_pages = int(request.form["numPages"])
            num_iter = int(request.form["iterno"])
            node_iter = int(request.form["itno"])
            # Add URL Validation
            spider_func(web_url, num_pages)
            sprank_func(domain=web_url, num_iterations=num_iter)
            spjson_func(domain=web_url, howmany=node_iter)
            flash('Visualizing Graph!', 'success')
            return render_template('index.html', title='Home', result=True)
        except KeyError:
            web_url = None

        try:
            web_url_node = request.form["webUrlnode"]
            perplex = int(request.form["perp"])
            embed_dimm = int(request.form["emb"])
            walk_length = int(request.form["node"])
            num_walks = int(request.form["walk"])
            window_size = int(request.form["window_size"])
            # Add URL Validation
            g, model = compute_embeddings(
                            url=web_url_node,
                            embedding_dimensions=embed_dimm,
                            walk_length=walk_length,
                            num_walks=num_walks,
                            window_size=window_size
                        )
            flash('Embedings Computed, Processing Visualizations!', 'success')
            get_viz(url=web_url_node, g=g, model=model, perplexity=perplex)
            file_path = web_url_node.split('/')[2]
            return render_template('index.html', title='Home', result=True, graph_show=True, file_path=file_path)
        except KeyError:
            web_url_node = None

        error = 'Please try again! Not a valid Web URL'
        return render_template('index.html', error=error, result=False)
    else:
        return render_template('index.html', result=False)

@app.route('/existing', methods=['GET', 'POST'])
def view_existing():
    web_urls = [row[0].split('/')[2] for row in db.session.execute(
            'SELECT url from webs'
        ).fetchall()]

    if request.method == 'GET':
        return render_template('existing.html', web_urls=web_urls)

    elif request.method == 'POST':
        link = request.form["link"]
        return render_template('existing.html', web_urls=web_urls, graph_show=True, file_path=link)

    else:
        return render_template('existing.html', web_urls=web_urls)
