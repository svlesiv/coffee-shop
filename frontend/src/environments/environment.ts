export const environment = {
  production: false,
  apiServerUrl: 'http://127.0.0.1:5000', // the running FLASK api server url
  auth0: {
    url: 'dev-bvzlp059.us', // the auth0 domain prefix
    audience: 'drink', // the audience set for the auth0 app
    clientId: 'qk3LYH12z3nfFNbXWh2KvW7ahSWquSaG', // the client id generated for the auth0 app
    callbackURL: 'http://127.0.0.1:4200', // the base url of the running ionic application. 
  }
};
