import json


XDR_URL = 'https://api.xdrurl.com'


def load_test_data(json_path):
    with open(json_path) as f:
        return json.load(f)


def test_get_incident_list(requests_mock):
    from PaloAltoNetworks_XDR import get_incidents_command, Client

    get_incidents_list_response = load_test_data('./test_data/get_incidents_list.json')
    requests_mock.post(f'{XDR_URL}/public_api/v1/incidents/get_incidents/', json=get_incidents_list_response)

    client = Client(
        base_url=f'{XDR_URL}/public_api/v1'
    )
    args = {
        'incident_id_list': '1 day'
    }
    _, outputs, _ = get_incidents_command(client, args)

    expected_output = {
        'PaloAltoNetworksXDR.Incident(val.incident_id==obj.incident_id)': get_incidents_list_response.get('reply')
                                                                                                     .get('incidents')
    }
    assert expected_output == outputs


def test_fetch_incidents(requests_mock):
    from PaloAltoNetworks_XDR import fetch_incidents, Client

    get_incidents_list_response = load_test_data('./test_data/get_incidents_list.json')
    requests_mock.post(f'{XDR_URL}/public_api/v1/incidents/get_incidents/', json=get_incidents_list_response)

    client = Client(
        base_url=f'{XDR_URL}/public_api/v1'
    )

    next_run, incidents = fetch_incidents(client, '3 month', {})

    assert len(incidents) == 2
    assert incidents[0]['name'] == "#1 - 'Local Analysis Malware' generated by XDR Agent detected on host AAAAA " \
                                   "involving user Administrator"

    assert incidents[1]['name'] == "#2 - 'Local Analysis Malware' generated by XDR Agent detected on host BBBBB " \
                                   "involving user Administrator"

    assert incidents[0]['rawJSON'] == json.dumps(get_incidents_list_response['reply']['incidents'][0])


def test_get_incident_extra_data(requests_mock):
    from PaloAltoNetworks_XDR import get_incident_extra_data_command, Client

    get_incident_extra_data_response = load_test_data('./test_data/get_incident_extra_data.json')
    requests_mock.post(f'{XDR_URL}/public_api/v1/incidents/get_incident_extra_data/',
                       json=get_incident_extra_data_response)

    client = Client(
        base_url=f'{XDR_URL}/public_api/v1'
    )
    args = {
        'incident_id': '1'
    }
    _, outputs, _ = get_incident_extra_data_command(client, args)

    expected_incident = get_incident_extra_data_response.get('reply').get('incident')

    expected_incident.update({
        'alerts': get_incident_extra_data_response.get('reply').get('alerts').get('data'),
        'network_artifacts': get_incident_extra_data_response.get('reply').get('network_artifacts').get('data', []),
        'file_artifacts': get_incident_extra_data_response.get('reply').get('file_artifacts').get('data')
    })

    expected_output = {
        'PaloAltoNetworksXDR.Incident(val.incident_id==obj.incident_id)': expected_incident
    }
    assert expected_output == outputs


def test_update_incident(requests_mock):
    from PaloAltoNetworks_XDR import update_incident_command, Client

    update_incident_response = load_test_data('./test_data/update_incident.json')
    requests_mock.post(f'{XDR_URL}/public_api/v1/incidents/update_incident/', json=update_incident_response)

    client = Client(
        base_url=f'{XDR_URL}/public_api/v1'
    )
    args = {
        'incident_id': '1',
        'status': 'new'
    }
    readable_output, outputs, _ = update_incident_command(client, args)

    assert outputs is None
    assert readable_output == 'Incident 1 has been updated'


def test_get_endpoints(requests_mock):
    from PaloAltoNetworks_XDR import get_endpoints_command, Client

    get_endpoints_response = load_test_data('./test_data/get_endpoints.json')
    requests_mock.post(f'{XDR_URL}/public_api/v1/endpoints/get_endpoint/', json=get_endpoints_response)

    client = Client(
        base_url=f'{XDR_URL}/public_api/v1'
    )
    args = {
        'hostname': 'foo',
        'page': 1,
        'limit': 3
    }

    _, outputs, _ = get_endpoints_command(client, args)
    expected_output = {
        'PaloAltoNetworksXDR.Endpoint(val.endpoint_id == val.endpoint_id)': get_endpoints_response.get('reply')
                                                                                                  .get('endpoints')
    }
    assert expected_output == outputs


def test_insert_parsed_alert(requests_mock):
    from PaloAltoNetworks_XDR import insert_parsed_alert_command, Client

    insert_alerts_response = load_test_data('./test_data/create_alerts.json')
    requests_mock.post(f'{XDR_URL}/public_api/v1/alerts/insert_parsed_alerts/', json=insert_alerts_response)

    client = Client(
        base_url=f'{XDR_URL}/public_api/v1'
    )
    args = {
        "product": "VPN & Firewall-1",
        "vendor": "Check Point",
        "local_ip": "192.168.1.254",
        "local_port": "35398",
        "remote_ip": "0.0.0.0",
        "remote_port": "0",
        "event_timestamp": "1543270652000",
        "severity": "Low",
        "alert_name": "Alert Name Example",
        "alert_description": "Alert Description"
    }

    readable_output, outputs, _ = insert_parsed_alert_command(client, args)
    assert outputs is None
    assert readable_output == 'Alert inserted successfully'


def test_isolate_endpoint(requests_mock):
    from PaloAltoNetworks_XDR import isolate_endpoint_command, Client

    requests_mock.post(f'{XDR_URL}/public_api/v1/endpoints/get_endpoint/', json={
        'reply': {
            'endpoints': [
                {
                    'endpoint_id': '1111'
                }
            ]
        }
    })

    isolate_endpoint_response = load_test_data('./test_data/isolate_endpoint.json')
    requests_mock.post(f'{XDR_URL}/public_api/v1/endpoints/isolate', json=isolate_endpoint_response)

    client = Client(
        base_url=f'{XDR_URL}/public_api/v1'
    )

    args = {
        "endpoint_id": "1111"
    }

    readable_output, outputs, _ = isolate_endpoint_command(client, args)
    assert outputs is None
    assert readable_output == 'Endpoint 1111 has isolated successfully'


def test_unisolate_endpoint(requests_mock):
    from PaloAltoNetworks_XDR import unisolate_endpoint_command, Client

    requests_mock.post(f'{XDR_URL}/public_api/v1/endpoints/get_endpoint/', json={
        'reply': {
            'endpoints': [
                {
                    'endpoint_id': '1111'
                }
            ]
        }
    })

    unisolate_endpoint_response = load_test_data('./test_data/unisolate_endpoint.json')
    requests_mock.post(f'{XDR_URL}/public_api/v1/endpoints/unisolate', json=unisolate_endpoint_response)

    client = Client(
        base_url=f'{XDR_URL}/public_api/v1'
    )

    args = {
        "endpoint_id": "1111"
    }

    readable_output, outputs, _ = unisolate_endpoint_command(client, args)
    assert outputs is None
    assert readable_output == 'Endpoint 1111 has un-isolated successfully'


def test_get_distribution_url(requests_mock):
    from PaloAltoNetworks_XDR import get_distribution_url_command, Client

    get_distribution_url_response = load_test_data('./test_data/get_distribution_url.json')
    requests_mock.post(f'{XDR_URL}/public_api/v1/distributions/get_dist_url/', json=get_distribution_url_response)

    client = Client(
        base_url=f'{XDR_URL}/public_api/v1'
    )

    args = {
        'distribution_id': '1111',
        'package_type': 'x86'
    }

    readable_output, outputs, _ = get_distribution_url_command(client, args)
    expected_url = get_distribution_url_response.get('reply').get('distribution_url')
    assert outputs == {
        'PaloAltoNetworksXDR.Distribution(val.id == obj.id)': {
            'id': '1111',
            'url': expected_url
        }
    }

    assert readable_output == f'[Distribution URL]({expected_url})'


def test_get_audit_management_logs(requests_mock):
    from PaloAltoNetworks_XDR import get_audit_management_logs_command, Client

    get_audit_management_logs_response = load_test_data('./test_data/get_audit_management_logs.json')
    requests_mock.post(f'{XDR_URL}/public_api/v1/audits/management_logs/', json=get_audit_management_logs_response)

    client = Client(
        base_url=f'{XDR_URL}/public_api/v1'
    )

    args = {
        'email': 'woo@demisto.com',
        'limit': '3',
        'timestamp_gte': '3 month'
    }

    readable_output, outputs, _ = get_audit_management_logs_command(client, args)

    expected_outputs = get_audit_management_logs_response.get('reply').get('data')
    assert outputs['PaloAltoNetworksXDR.AuditManagementLogs(val.AUDIT_ID == obj.AUDIT_ID)'] == expected_outputs


def test_get_audit_agent_reports(requests_mock):
    from PaloAltoNetworks_XDR import get_audit_agent_reports_command, Client

    get_audit_agent_reports_response = load_test_data('./test_data/get_audit_agent_report.json')
    requests_mock.post(f'{XDR_URL}/public_api/v1/audits/agents_reports/', json=get_audit_agent_reports_response)

    client = Client(
        base_url=f'{XDR_URL}/public_api/v1'
    )

    args = {
        'endpoint_names': 'woo.demisto',
        'limit': '3',
        'timestamp_gte': '3 month'
    }

    readable_output, outputs, _ = get_audit_agent_reports_command(client, args)
    expected_outputs = get_audit_agent_reports_response.get('reply').get('data')
    assert outputs['PaloAltoNetworksXDR.AuditAgentReports'] == expected_outputs


def test_insert_cef_alerts(requests_mock):
    from PaloAltoNetworks_XDR import insert_cef_alerts_command, Client

    insert_cef_alerts_response = load_test_data('./test_data/insert_cef_alerts.json')
    requests_mock.post(f'{XDR_URL}/public_api/v1/alerts/insert_cef_alerts/', json=insert_cef_alerts_response)

    client = Client(
        base_url=f'{XDR_URL}/public_api/v1'
    )

    args = {
        'cef_alerts': [
            'CEF:0|Check Point|VPN-1 & FireWall-1|Check Point|Log|microsoft-ds|Unknown|act=AcceptdeviceDirection=0 '
            'rt=1569477512000 spt=56957 dpt=445 cs2Label=Rule Name cs2=ADPrimery '
            'layer_name=FW_Device_blackened Securitylayer_uuid=07693fc7-1a5c-4f31-8afe-77ae96c71b8c match_id=1806 '
            'parent_rule=0rule_action=Accept rule_uid=8e45f36b-d106-4d81-a1f0-9d1ed9a6be5c ifname=bond2logid=0 '
            'loguid={0x5d8c5388,0x61,0x29321fac,0xc0000022} origin=1.1.1.1originsicname=CN=DWdeviceBlackend,'
            'O=Blackend sequencenum=363 version=5dst=1.1.1.1 inzone=External outzone=Internal product=VPN-1 & '
            'FireWall-1 proto=6service_id=microsoft-ds src=1.1.1.1',

            'CEF:0|Check Point|VPN-1 & FireWall-1|Check Point|Log|Log|Unknown|act=AcceptdeviceDirection=0 '
            'rt=1569477501000 spt=63088 dpt=5985 cs2Label=Rule Namelayer_name=FW_Device_blackened Securitylayer_'
            'uuid=07693fc7-1a5c-4f31-8afe-77ae96c71b8c match_id=8899 parent_rule=0rule_action=Accept rule_'
            'uid=ae987933-82c0-470f-ab1c-1ad552c82369conn_direction=Internal ifname=bond1.12 '
            'logid=0loguid={0x5d8c537d,0xbb,0x29321fac,0xc0000014} origin=1.1.1.1originsicname=CN=DWdeviceBlackend,'
            'O=Blackend sequencenum=899 version=5dst=1.1.1.1 product=VPN-1 & FireWall-1 proto=6 src=1.1.1.1'
        ]
    }

    readable_output, _, _ = insert_cef_alerts_command(client, args)

    assert readable_output == 'Alerts inserted successfully'


def test_get_distribution_status(requests_mock):
    from PaloAltoNetworks_XDR import get_distribution_status_command, Client

    get_distribution_status_response = load_test_data('./test_data/get_distribution_status.json')
    requests_mock.post(f'{XDR_URL}/public_api/v1/distributions/get_status/', json=get_distribution_status_response)

    client = Client(
        base_url=f'{XDR_URL}/public_api/v1'
    )

    args = {
        "distribution_ids": "588a56de313549b49d70d14d4c1fd0e3"
    }

    readable_output, outputs, _ = get_distribution_status_command(client, args)

    assert outputs == {
        'PaloAltoNetworksXDR.Distribution(val.id == obj.id)': [
            {
                'id': '588a56de313549b49d70d14d4c1fd0e3',
                'status': 'Completed'
            }
        ]
    }


def test_get_distribution_versions(requests_mock):
    from PaloAltoNetworks_XDR import get_distribution_versions_command, Client

    get_distribution_versions_response = load_test_data('./test_data/get_distribution_versions.json')
    requests_mock.post(f'{XDR_URL}/public_api/v1/distributions/get_versions/', json=get_distribution_versions_response)

    client = Client(
        base_url=f'{XDR_URL}/public_api/v1'
    )

    readable_output, outputs, _ = get_distribution_versions_command(client)

    assert outputs == {
        'PaloAltoNetworksXDR.DistributionVersions': {
            "windows": [
                "7.0.0.27797"
            ],
            "linux": [
                "7.0.0.1915"
            ],
            "macos": [
                "7.0.0.1914"
            ]
        }
    }


def test_create_distribution(requests_mock):
    from PaloAltoNetworks_XDR import create_distribution_command, Client

    create_distribution_response = load_test_data('./test_data/create_distribution.json')
    requests_mock.post(f'{XDR_URL}/public_api/v1/distributions/create/', json=create_distribution_response)

    client = Client(
        base_url=f'{XDR_URL}/public_api/v1'
    )

    args = {
        "name": "dfslcxe",
        "platform": "windows",
        "package_type": "standalone",
        "agent_version": "7.0.0.28644"
    }

    readable_output, outputs, _ = create_distribution_command(client, args)

    expected_distribution_id = create_distribution_response.get('reply').get('distribution_id')
    assert outputs == {
        'PaloAltoNetworksXDR.Distribution(val.id == obj.id)': {
            'id': expected_distribution_id,
            "name": "dfslcxe",
            "platform": "windows",
            "package_type": "standalone",
            "agent_version": "7.0.0.28644",
            'description': None
        }
    }
    assert readable_output == f'Distribution {expected_distribution_id} created successfully'
